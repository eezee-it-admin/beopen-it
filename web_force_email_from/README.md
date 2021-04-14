# Force Email from

The param "mail.catchall.domain" should be exists

Don't forget to remove the param "mail.bounce.alias" if you want use the "mail.default.bounce.alias"

```xml
<delete model="ir.config_parameter" search="[('id','=', ref('mail.icp_mail_bounce_alias'))]"/>
``
