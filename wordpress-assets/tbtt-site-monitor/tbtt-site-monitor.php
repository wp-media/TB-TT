<?php
/**
 * Plugin Name: TB-TT Site Monitor
 * Description: Forces WP Rocket auto-updates and exposes a REST route reporting pending-update
 *              state for TB-TT's health monitoring.
 * Version: 1.1.0
 * Author: WP Media
 * License: GPL-2.0-or-later
 *
 * Install as a regular plugin (wp-content/plugins/tbtt-site-monitor/) and activate it on each TB-TT test site.
 *
 * Core update channel (nightly/beta/point release) is set manually per site via the "WordPress Beta
 * Tester" plugin (slug: wordpress-beta-tester) — this plugin no longer forces it. WP_AUTO_UPDATE_CORE
 * must still be set to true in wp-config.php so core updates actually auto-apply unattended.
 *
 * Unlike a must-use plugin, this one can be deactivated from wp-admin. If that happens, the REST
 * route below stops responding (404), which TB-TT's health check already reports as a failure.
 *
 * Some hosts strip the Authorization header before PHP sees it, which breaks Application Password
 * auth on the REST route below with a 401 that looks like a credentials problem. If that happens,
 * add a host-level fix (Apache: rewrite HTTP_AUTHORIZATION in .htaccess; Nginx: pass fastcgi_param
 * HTTP_AUTHORIZATION $http_authorization;).
 */

defined( 'ABSPATH' ) || exit;

add_filter(
	'auto_update_plugin',
	function ( $update, $item ) {
		if ( isset( $item->slug ) && 'wp-rocket' === $item->slug ) {
			return true;
		}
		return $update;
	},
	10,
	2
);

add_action(
	'rest_api_init',
	function () {
		register_rest_route(
			'tbtt-monitor/v1',
			'/updates-pending',
			array(
				'methods'             => 'GET',
				'callback'            => 'tbtt_site_monitor_get_updates_pending',
				'permission_callback' => function () {
					return current_user_can( 'update_plugins' ) && current_user_can( 'update_core' );
				},
			)
		);
	}
);

/**
 * Forces a fresh update check and reports pending core/plugin/theme updates.
 */
function tbtt_site_monitor_get_updates_pending() {
	require_once ABSPATH . 'wp-admin/includes/update.php';

	wp_version_check( array(), true );

	delete_site_transient( 'update_plugins' );
	wp_update_plugins();

	delete_site_transient( 'update_themes' );
	wp_update_themes();

	$plugin_updates = get_site_transient( 'update_plugins' );
	$theme_updates  = get_site_transient( 'update_themes' );
	$core_updates   = get_site_transient( 'update_core' );

	$plugins_pending = ( $plugin_updates && ! empty( $plugin_updates->response ) ) ? count( $plugin_updates->response ) : 0;
	$themes_pending  = ( $theme_updates && ! empty( $theme_updates->response ) ) ? count( $theme_updates->response ) : 0;

	$core_pending      = false;
	$core_response_type = null;
	if ( $core_updates && ! empty( $core_updates->updates ) ) {
		foreach ( $core_updates->updates as $offer ) {
			if ( isset( $offer->response ) && 'latest' !== $offer->response ) {
				$core_pending      = true;
				$core_response_type = $offer->response;
				break;
			}
		}
	}

	return new WP_REST_Response(
		array(
			'plugins_pending'    => $plugins_pending,
			'themes_pending'     => $themes_pending,
			'core_pending'       => $core_pending,
			'core_response_type' => $core_response_type,
		),
		200
	);
}
