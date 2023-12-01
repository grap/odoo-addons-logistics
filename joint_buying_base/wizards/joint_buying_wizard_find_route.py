# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from types import SimpleNamespace

from treelib import Tree

from odoo import api, fields, models

from ..models.res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingWizardFindRoute(models.TransientModel):
    _name = "joint.buying.wizard.find.route"
    _description = "Joint Buying Wizard Find Route"

    # 30 Days
    _MAX_TRANSPORT_DURATION = 30

    transport_request_id = fields.Many2one(
        string="Transport Request",
        comodel_name="joint.buying.transport.request",
        default=lambda x: x._default_transport_reqquest_id(),
        readonly=True,
        required=True,
        ondelete="cascade",
    )

    availability_date = fields.Datetime(
        related="transport_request_id.availability_date", readonly=True
    )

    start_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Origin",
        related="transport_request_id.start_partner_id",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        readonly=True,
    )

    destination_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Destination",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        related="transport_request_id.destination_partner_id",
        readonly=True,
    )

    tour_line_ids = fields.Many2many(
        comodel_name="joint.buying.tour.line",
        string="Tour Lines",
        compute="_compute_simulation",
    )

    tree_text = fields.Text(
        compute="_compute_simulation",
    )

    is_different_simulation = fields.Boolean(
        compute="_compute_simulation",
    )

    # #################
    # Default Section
    # #################
    def _default_transport_reqquest_id(self):
        return self.env.context.get("active_id")

    # #################
    # Compute Section
    # #################
    @api.depends("transport_request_id")
    def _compute_simulation(self):
        self.ensure_one()
        results = self.compute_tours(self.transport_request_id)
        result = results.get(self.transport_request_id)
        if result:
            tree, self.tour_line_ids = result
            self.tree_text = tree.show(stdout=False, line_type="ascii-em")
            self.is_different_simulation = (
                self.mapped("transport_request_id.line_ids.tour_line_id").ids
                != self.tour_line_ids.ids
            )

    @api.model
    def compute_tours(self, transport_requests):
        """Endtry point to compute the best way for a RecordSet of Transport Requests"""
        results = {}
        for transport_request in transport_requests:
            tree = self._populate_tree(transport_request)

            nodes = self.get_nodes_optimal_road(
                tree, transport_request.destination_partner_id
            )
            tour_lines = self.env["joint.buying.tour.line"]
            for node in [x for x in nodes if x.data.line]:
                tour_lines |= node.data.line
            results[transport_request] = tree, tour_lines

        return results

    # #################
    # UI Section
    # #################
    def button_apply(self):
        self.ensure_one()
        self.transport_request_id._set_tour_lines(self.tour_line_ids)

    # #################
    # Treelib Tools Section
    # #################
    @api.model
    def _create_initial_node(self, tree, partner, date):
        return tree.create_node(
            tag=f"{partner.joint_buying_code}-{date}-0-BEST_MAIN_NODE",
            data=SimpleNamespace(
                partner=partner, date=date, best_main_node=True, line=False
            ),
        )

    @api.model
    def _create_following_node(self, tree, parent, line, destination):

        partner = line.arrival_point_id
        date = line.arrival_date
        best_main_node = (
            line.arrival_point_id == destination
            or line.arrival_point_id.joint_buying_is_durable_storage
        )
        new_node = tree.create_node(
            parent=parent,
            tag=f"{partner.joint_buying_code}-{date}-{line.id}"
            f"{best_main_node and '-BEST_MAIN_NODE' or ''}",
            data=SimpleNamespace(
                partner=partner, date=date, best_main_node=best_main_node, line=line
            ),
        )

        best_nodes = [
            x
            for x in tree.all_nodes()
            if x.data.best_main_node and x.data.partner == line.arrival_point_id
        ]

        if len(best_nodes) > 1:
            the_best_node = self._get_best_node(best_nodes)
            for node in best_nodes:
                if node == the_best_node:
                    continue
                node.tag = node.tag.replace("-BEST_MAIN_NODE", "")
                node.data.best_main_node = False

        return new_node

    @api.model
    def _get_best_node(self, nodes):
        best_node = nodes[0]
        for node in nodes[1:]:
            if node.data.date < best_node.data.date:
                best_node = node
        return best_node

    @api.model
    def _get_startable_nodes(self, tree):
        """
        A (BEST)
        |======== B
        |         |===== C (BEST)
        |=============== C
                         |============ D (BEST)
        return : [A, C, D]
        """
        return [x for x in tree.all_nodes() if x.data.best_main_node]

    @api.model
    def get_nodes_optimal_road(self, tree, destination_partner_id):
        """
        A
        |== B
        |   |== C
        |========== D
        - If the destination is C, return [A, B, C]
        - If the destination is D, return [A, D]
        """
        destination_nodes = [
            x for x in tree.all_nodes() if x.data.partner == destination_partner_id
        ]
        if not destination_nodes:
            return []
        destination_node = destination_nodes[0]

        result = [tree[x] for x in tree.rsearch(destination_node.identifier)]
        result.reverse()
        return result

    # #################
    # Tree creation / Update Section
    # #################
    @api.model
    def _populate_tree(self, transport_request):
        # Get all the tours subsequent to the transport request for a given period of time
        max_date = transport_request.availability_date + datetime.timedelta(
            days=self._MAX_TRANSPORT_DURATION
        )
        tours = self.env["joint.buying.tour"].search(
            [
                ("start_date", ">=", transport_request.availability_date),
                ("start_date", "<=", max_date),
            ],
            order="start_date",
        )

        # Initialize Tree
        tree = Tree()
        self._create_initial_node(
            tree,
            transport_request.start_partner_id,
            transport_request.availability_date,
        )

        # We go through all the tours, in ascending date order
        for tour in tours:
            # we select the places (nodes) where the merchandise can be
            startable_nodes = self._get_startable_nodes(tree)
            for startable_node in startable_nodes:
                for line in tour.line_ids.filtered(
                    lambda x: x.sequence_type == "journey"
                    and startable_node.data.date <= x.start_date
                    and startable_node.data.partner == x.starting_point_id
                ):
                    found_lines = self._get_interesting_route(
                        tour=tour,
                        from_line=line,
                        destination=transport_request.destination_partner_id,
                        # We don't want to target origin
                        # you don't want to go round and round in the same place.
                        excludes=[
                            transport_request.start_partner_id,
                            startable_node.data.partner,
                        ],
                    )
                    if found_lines:
                        current_node = startable_node
                        for found_line in found_lines:
                            current_node = self._create_following_node(
                                tree,
                                current_node,
                                found_line,
                                transport_request.destination_partner_id,
                            )

                            # we've arrived at our destination!
                            if (
                                found_line.arrival_point_id
                                == transport_request.destination_partner_id
                            ):
                                return tree

        return tree

    @api.model
    def _get_interesting_route(self, tour, from_line, destination, excludes):
        # we try to go the destination
        available_lines = [
            x
            for x in tour.line_ids.filtered(
                lambda x: x.start_date >= from_line.start_date
                and x.sequence_type == "journey"
            )
        ]

        # The destination is present in the available lines, directly return
        if destination in [x.arrival_point_id for x in available_lines]:
            return available_lines

        # We start from the end, and we remove uninteresting lines
        # If an arrival is interesting, we keep all the journey
        # from the from_line to the arrival
        available_lines.reverse()

        result = []
        to_select = False
        for line in available_lines:
            if to_select or (
                line.arrival_point_id.joint_buying_is_durable_storage
                and line.arrival_point_id not in excludes
            ):
                result.append(line)
                to_select = True
        result.reverse()
        return result
