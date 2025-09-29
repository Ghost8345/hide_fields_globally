from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_test_condition = fields.Boolean(
        string="Is Test Condition",
        compute='_compute_is_test_condition',
        help="A test field to check conditional logic for hiding other fields."
    )


    def _compute_is_test_condition(self):
        """ The 'compute' method reads the value from our storage field. """
        for partner in self:
            partner.is_test_condition = False


