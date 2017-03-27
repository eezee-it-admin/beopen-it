def migrate(cr, version):
    # Changes for botc_markettype
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