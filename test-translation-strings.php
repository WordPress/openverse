<?php
/**
 * Testing if Glotpress automatically pulls translation strings from PHP files in the repo.
 *
 * For reference:
 */

/**
 * Retrieve translated string with gettext context.
 *
 * Quite a few times, there will be collisions with similar translatable text
 * found in more than two places, but with different translated context.
 *
 * By including the context in the pot file, translators can translate the two
 * strings differently.
 *
 * @since 2.8.0
 *
 * @param string $text    Text to translate.
 * @param string $context Context information for the translators.
 * @param string $domain  Optional. Text domain. Unique identifier for retrieving translated strings.
 *                        Default 'default'.
 * @return string Translated context string without pipe.
 */
// function _x( $text, $context, $domain = 'default' ) {
//         return translate_with_gettext_context( $text, $context, $domain );
// }


_x( 'Hello world', 'Initial test string', 'wp-openverse' );
