<?php defined('ABSPATH') or die('Access denied.'); ?>

<div class="row wdt-constructor-step" data-step="1">
    <h4 class="m-b-20 p-l-15 f-15">
        <?php _e('Choose what kind of table would you like to construct', 'wpdatatables'); ?>
    </h4>

    <?php if (Connection::enabledSeparate()) { ?>
    <div class="col-sm-2 p-l-15">
        <!-- Separate connection -->
        <h4 class="c-black m-b-20">
            <?php _e('
                                Connection', 'wpdatatables'); ?>
            <i class="zmdi zmdi-help-outline" data-toggle="tooltip" data-placement="right"
               title="<?php _e('Use separate connection', 'wpdatatables'); ?>"></i>
        </h4>
        <!-- input source type selection -->
        <div class="form-group">
            <div class="fg-line">
                <div class="select">
                    <select class="selectpicker" id="wdt-constructor-table-connection">
                        <option value="">WP Connection</option>
                        <?php foreach (Connection::getAll() as $key => $wdtSeparateConnection) { ?>
                            <option data-vendor='<?php echo $wdtSeparateConnection['vendor'] ?>' value="<?php echo $wdtSeparateConnection['id'] ?>" <?php echo $wdtSeparateConnection['default'] ? 'selected' : '' ?>><?php echo $wdtSeparateConnection['name'] ?></option>
                        <?php } ?>
                    </select>
                </div>
            </div>
        </div>
        <!-- /Server side processing toggle -->
    </div>
    <?php
    } else {
    ?>
        <input type="hidden" id="wdt-constructor-table-connection" value="">
    <?php
    }
    ?>

    <div class="col-sm-12 p-0">

        <div class="wdt-constructor-type-selecter-block col-sm-2">
            <div class="card" data-value="source">
                <div class="card-header">
                    <div class="wdt-constructor-overlay"></div>
                    <img class="img-responsive"
                         src="<?php echo WDT_ASSETS_PATH ?>img/constructor/add-from-data-source.png">
                </div>
                <div class="card-body">
                    <h4 class="f-14"><?php _e('Create a table linked to an existing data source', 'wpdatatables'); ?>.</h4>
                    <span><?php _e('(Excel, CSV, Google Spreadsheet, SQL query, XML, JSON, serialized PHP array). Data will be read from the source every time on page load. Only SQL-based tables can be made editable.', 'wpdatatables'); ?></span>
                </div>
            </div>
        </div>

        <div class="wdt-constructor-type-selecter-block col-sm-2">
            <div class="card" data-value="manual">
                <div class="card-header">
                    <div class="wdt-constructor-overlay"></div>
                    <img class="img-responsive" src="<?php echo WDT_ASSETS_PATH ?>img/constructor/manual.png">
                </div>
                <div class="card-body">
                    <h4 class="f-14"><?php _e('Create a table manually', 'wpdatatables'); ?>.</h4>
                    <span><?php _e('Define the number and type of columns, and fill in the data manually in WP admin. Table will be stored in database and can be edited from WP admin, or made front-end editable.', 'wpdatatables'); ?></span>
                </div>
            </div>
        </div>

        <div class="wdt-constructor-type-selecter-block col-sm-2">
            <div class="card" data-value="file">
                <div class="card-header">
                    <div class="wdt-constructor-overlay"></div>
                    <img class="img-responsive"
                         src="<?php echo WDT_ASSETS_PATH ?>img/constructor/import-data-from-data-source.png">
                </div>
                <div class="card-body">
                    <h4 class="f-14"><?php _e('Create a table by importing data from data source', 'wpdatatables'); ?>.</h4>
                    <span><?php _e('(Excel, CSV, Google Spreadsheet). Data will be imported to database, the table can be edited in WP admin, or made front-end editable.', 'wpdatatables'); ?></span>
                </div>
            </div>
        </div>

        <div class="wdt-constructor-type-selecter-block col-sm-2">
            <div class="card" data-value="wp">
                <div class="card-header">
                    <div class="wdt-constructor-overlay"></div>
                    <img class="img-responsive"
                         src="<?php echo WDT_ASSETS_PATH ?>img/constructor/generate-query-to-wordpress-database.png">
                </div>
                <div class="card-body">
                    <h4 class="f-14"><?php _e('Generate a query to WordPress database', 'wpdatatables'); ?>.</h4>
                    <span><?php _e('Create a MySQL-query-based table by generating a query to WordPress database (posts, taxonomies, postmeta) with a GUI tool.', 'wpdatatables'); ?></span>
                </div>
            </div>
        </div>

        <div class="wdt-constructor-type-selecter-block col-sm-2">
            <div class="card" data-value="mysql">
                <div class="card-header">
                    <div class="wdt-constructor-overlay"></div>
                    <img class="img-responsive"
                         src="<?php echo WDT_ASSETS_PATH ?>img/constructor/generate-query-to-mysql-database.png">
                </div>
                <div class="card-body">
                    <h4 class="f-14"><?php _e('Generate a query to MySQL database', 'wpdatatables'); ?>.</h4>
                    <span><?php _e('Create a SQL-query-based table by generating a query to any custom SQL database with a GUI tool.', 'wpdatatables'); ?></span>
                </div>
            </div>
        </div>

    </div>

</div>