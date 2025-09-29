import logging
from lxml import etree
from odoo import models, api

_logger = logging.getLogger(__name__)

_cached_hidden_fields = None


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_all_hidden_fields(self):
        """ Retrieves hidden fields and their conditions from the config model. """
        global _cached_hidden_fields
        if _cached_hidden_fields is not None:
            return _cached_hidden_fields

        config_records = self.env['ir.model.fields.hidden'].search([])
        result = {}
        for config in config_records:
            model_name = config.field_id.model
            field_name = config.field_id.name
            condition_name = config.condition_field_id.name if config.condition_field_id else None

            model_configs = result.setdefault(model_name, [])
            model_configs.append({'hide': field_name, 'condition': condition_name})

        _cached_hidden_fields = result
        return result

    @api.model
    def _clear_hidden_fields_cache(self):
        """ Clears the cache when the hidden fields configuration changes. """
        global _cached_hidden_fields
        _cached_hidden_fields = None

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)

        all_hidden_fields = self._get_all_hidden_fields()

        if not all_hidden_fields.get(self._name) or arch is None:
            return arch, view

        try:
            # This check is crucial. It ensures the logic only runs on views that
            # display record data, preventing errors in search panels and other components.
            if view_type in ('form', 'list', 'kanban'):
                doc = arch
                configs_for_current_model = all_hidden_fields.get(self._name, [])

                # The XPath targets both fields and their associated labels.
                for node in doc.xpath('//field | //label[@for]'):
                    field_name = node.get('name') or node.get('for')
                    if not field_name:
                        continue

                    for config in configs_for_current_model:
                        if config['hide'] == field_name:
                            # Apply conditional logic if a condition is set
                            if config['condition']:
                                condition_field_name = config['condition']
                                node.set('invisible', condition_field_name)
                                # # For list/tree views, also set 'column_invisible' with the correct domain syntax
                                if view_type in ('tree', 'list'):
                                    domain_string = f"[('{condition_field_name}', '=', True)]"
                                    node.set('column_invisible', domain_string)

                                # Ensure the condition field's data is available to the client.
                                # Check if the condition field is already in the view.
                                if not doc.xpath(f"//field[@name='{condition_field_name}']"):
                                    # If not, add it as an invisible field.
                                    new_node = etree.Element('field', name=condition_field_name, invisible='1', column_invisible='1')
                                    node.addnext(new_node)
                            else:
                                # Apply permanent invisibility if no condition is set
                                node.set('invisible', '1')
                                node.set('column_invisible', '1')

                            # A rule was applied, so we can stop checking configs for this node.
                            break

        except Exception as e:
            _logger.error(f"Error in custom _get_view while hiding fields: {e}", exc_info=True)

        return arch, view

