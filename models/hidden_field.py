from odoo import api, models, fields

class HiddenField(models.Model):
    _name = "ir.model.fields.hidden"
    _description = "Hidden Fields Configuration"

    field_id = fields.Many2one(
        "ir.model.fields",
        string="Hidden Field",
        required=True,
        ondelete="cascade", # If the field is deleted from Odoo, remove this config
    )

    condition_field_id = fields.Many2one(
        "ir.model.fields",
        string="Condition Field",
        help="If set, the field will be hidden only when this boolean field is true.",
        # This domain ensures users can only select a boolean field from the same model
        domain="[('model_id', '=', model_id), ('ttype', '=', 'boolean')]"
    )

    # This invisible field will make the domain on condition_field_id work
    model_id = fields.Many2one(related='field_id.model_id')

    _sql_constraints = [
        ('field_unique', 'unique(field_id)', 'This field is already marked as hidden.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        # Clear the cache after creating new hidden field entries
        self.env['base']._clear_hidden_fields_cache()
        return res

    def write(self, vals):
        res = super().write(vals)
        # Clear the cache after updating hidden field entries
        self.env['base']._clear_hidden_fields_cache()
        return res

    def unlink(self):
        res = super().unlink()
        # Clear the cache after deleting hidden field entries
        self.env['base']._clear_hidden_fields_cache()
        return res