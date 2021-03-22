tables = {'products': [('product_id', 'varchar PRIMARY KEY'), ('brand', 'varchar'), ('category', 'varchar'),
                       ('color', 'varchar'), ('deeplink', 'varchar'), ('description', 'varchar'),
                       ('fast_mover', 'boolean'), ('flavor', 'varchar'), ('gender', 'varchar'),
                       ('herhaalaankopen', 'boolean'), ('name', 'varchar'), ('predict_out_of_stock_date', 'varchar'),
                       ('recommendable', 'boolean'), ('size', 'varchar')],
          'product_prices': [('product_id varchar', 'PRIMARY KEY'), ('discount', 'float'), ('mrsp', 'float'),
                             ('selling_price', 'float')],
          'product_categories': [('product_id', 'varchar PRIMARY KEY'), ('category', 'varchar'),
                                 ('sub_category', 'varchar'), ('sub_sub_category', 'varchar'),
                                 ('sub_sub_sub_category', 'varchar'), ],
          'product_properties': [('product_id', 'varchar PRIMARY KEY'), ('availability', 'varchar NULL'),
                                 ('bundel_sku', 'varchar NULL'), ('discount', 'varchar NULL'),
                                 ('doelgroep', 'varchar NULL'), ('eenheid', 'varchar NULL'), ('factor', 'varchar NULL'),
                                 ('folder_actief', 'varchar NULL'), ('gebruik', 'varchar NULL'),
                                 ('geschiktvoor', 'varchar NULL'), ('geursoort', 'varchar NULL'),
                                 ('huidconditie', 'varchar NULL'), ('huidtype', 'varchar NULL'),
                                 ('huidtypegezicht', 'varchar NULL'), ('inhoud', 'varchar NULL'),
                                 ('klacht', 'varchar NULL'), ('kleur', 'varchar NULL'), ('leeftijd', 'varchar NULL'),
                                 ('mid', 'varchar NULL'), ('online_only', 'varchar NULL'), ('serie', 'varchar NULL'),
                                 ('shopcart_promo_item', 'varchar NULL'), ('shopcart_promo_price', 'varchar NULL'),
                                 ('soort', 'varchar NULL'), ('soorthaarverzorging', 'varchar NULL'),
                                 ('soortmondverzorging', 'varchar NULL'), ('sterkte', 'varchar NULL'),
                                 ('stock', 'varchar NULL'), ('tax', 'varchar NULL'), ('type', 'varchar NULL'),
                                 ('typehaarkleuring', 'varchar NULL'), ('typetandenborstel', 'varchar NULL'),
                                 ('variant', 'varchar NULL'), ('waterproof', 'varchar NULL'), ('weekdeal', 'boolean'),
                                 ('weekdeal_from', 'varchar NULL'), ('weekdeal_to', 'varchar NULL')],
          'product_sm': [('product_id', 'varchar PRIMARY KEY'), ('last_updated', 'timestamp'), ('type', 'varchar'),
                         ('is_active', 'boolean')],
          'product_in_order': [('session_id', 'varchar'), (
                                'product_id', 'varchar, PRIMARY KEY(session_id, product_id)')],
          'order_dates': [('session_id varchar', 'PRIMARY KEY'), ('session_start', 'timestamp'), ('session_end', 'timestamp')]

          }



