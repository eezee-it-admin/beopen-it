from odoo import SUPERUSER_ID
from odoo.api import Environment

def migrate(cr, version):

    env = Environment(cr, SUPERUSER_ID, {})

    products_object = env["product.product"]

    #Get all markettypes and create product for each of them
    cr.execute('SELECT id, name, description, price, currency_id, code from botc_markettype')

    for markettype_id, name, description, price, currency_id, code in cr.fetchall():

        product_values = {
            "name": name,
            "sale_ok": True,
            "purchase_ok": False,
            "list_price": price,
            "lst_price": price,
            "currency_id": currency_id,
            "type": "service",
            "recurring_invoice": True,
            "default_code": code
        }

        product = products_object.create(product_values)

        if product:
            cr.execute('UPDATE botc_markettype SET product_template_id = %s where id = %s', (product.product_tmpl_id.id, markettype_id,))


    #Get all modules and create product for each of them
    cr.execute('SELECT id, name, description, price, currency_id, image from botc_module where active = True')

    for module_id, name, description, price, currency_id, image in cr.fetchall():

        product_values = {
            "name": name,
            "description": description,
            "description_sale": "%s module" % name,
            "sale_ok": True,
            "purchase_ok": False,
            "list_price": price,
            "lst_price": price,
            "currency_id": currency_id,
            "type": "service",
            "recurring_invoice": True,
            "image": image
        }

        product = products_object.create(product_values)

        if product:
            cr.execute('UPDATE botc_module SET product_template_id = %s where id = %s', (product.product_tmpl_id.id, module_id,))


    #Get all services and create product for each of them
    cr.execute('SELECT id, name, description, price, currency_id, fixed_price, unit, image from botc_service where active = True')

    for service_id, name, description, price, currency_id, fixed_price, unit, image in cr.fetchall():

        product_values = {
            "name": ("%s %s" % (name, unit)).strip(" "),
            "sale_ok": True,
            "purchase_ok": False,
            "list_price": price,
            "lst_price": price,
            "currency_id": currency_id,
            "type": "service",
            "image": image
        }
        if fixed_price:
            product_values["recurring_invoice"] = False
        else:
            product_values["recurring_invoice"] = True

        product = products_object.create(product_values)

        if product:
            cr.execute('UPDATE botc_service SET product_template_id = %s where id = %s', (product.product_tmpl_id.id, service_id,))




    cr.execute('ALTER TABLE BOTC_MARKETTYPE DROP CONSTRAINT IF EXISTS botc_markettype_currency_id_fkey')

    cr.execute('ALTER TABLE BOTC_MARKETTYPE DROP COLUMN IF EXISTS currency_id')

    cr.execute('ALTER TABLE BOTC_MARKETTYPE DROP COLUMN IF EXISTS price')

    #Changes for botc_module
    cr.execute('ALTER TABLE botc_module DROP CONSTRAINT IF EXISTS botc_module_currency_id_fkey')

    cr.execute('ALTER TABLE botc_module DROP COLUMN IF EXISTS currency_id')

    cr.execute('ALTER TABLE botc_module DROP COLUMN IF EXISTS price')


    # Changes for botc_service
    cr.execute('ALTER TABLE botc_service DROP CONSTRAINT IF EXISTS botc_service_currency_id_fkey')

    cr.execute('ALTER TABLE botc_service DROP COLUMN IF EXISTS currency_id')

    cr.execute('ALTER TABLE botc_service DROP COLUMN IF EXISTS price')
