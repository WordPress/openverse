<?php
/**
 * Head & Footer Code plugin for WordPress
 *
 * @package     Head_Footer_Code
 * @since       1.0.0
 * @author      Aleksandar Urošević
 * @link        https://urosevic.net/
 * @link        https://www.techwebux.com/
 *
 * Plugin Name: Head & Footer Code
 * Plugin URI:  https://urosevic.net/wordpress/plugins/head-footer-code/
 * Description: Easy add site-wide, category or article specific custom code before the closing <strong>&lt;/head&gt;</strong> and <strong>&lt;/body&gt;</strong> or after opening <strong>&lt;body&gt;</strong> HTML tag.
 * Version:     1.5.7
 * Author:      Aleksandar Urošević
 * Author URI:  https://urosevic.net/
 * License:     GPLv3
 * License URI: https://www.gnu.org/licenses/gpl-3.0.txt
 * Text Domain: head-footer-code
 * Requires at least: 5.2
 * Tested up to: 7.0
 * Requires PHP: 5.6
 */

// If this file is called directly, abort.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'HFC__MIN_PHP', '5.6' );
define( 'HFC__MIN_WP', '5.2' );

define( 'HFC_VER', '1.5.7' );
define( 'HFC_VER_DB', '11' );
define( 'HFC_FILE', __FILE__ );

register_activation_hook( HFC_FILE, array( '\Techwebux\Hfc\Main', 'plugin_activation' ) );

require_once __DIR__ . '/classes/autoload.php';
new \Techwebux\Hfc\Main();
