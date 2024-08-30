from textwrap import dedent

import pytest

from data_refresh.remap_table_constraints import (
    ConstraintInfo,
    generate_constraints_for_table,
)


@pytest.mark.parametrize(
    "all_constraints, table_name, temp_table_name, expected_alter_statements",
    [
        # No constraints
        ([], "audio", "temp_import_audio", []),
        (
            [
                # Constraint that does not apply to or reference the table_name table
                ConstraintInfo(
                    "image", "irrelevant_constraint", "CHECK (char_length(foo) = 5)"
                ),
                # Foreign key constraint that does not apply to or reference the table_name table
                ConstraintInfo(
                    "imagelist_images",
                    "imagelist_images_image_id_fkey",
                    "FOREIGN KEY (image_id) REFERENCES image(id) DEFERRABLE INITIALLY DEFERRED",
                ),
                # Primary key constraint; no alters should be generated
                ConstraintInfo("audio", "audio_pkey", "PRIMARY KEY (id)"),
                # Unique constraint; no alters should be generated
                ConstraintInfo("audio", "audio_url_key", "UNIQUE (url)"),
                # Constraint that applies to the table_name and should have alters generated
                ConstraintInfo(
                    "audio",
                    "example_check_constraint",
                    "CHECK (char_length(title) > 5)",
                ),
                # Foreign key constraint for which alters and drop_orphans should be generated
                ConstraintInfo(
                    "audiolist_audios",
                    "audiolist_audios_audio_id_fkey",
                    "FOREIGN KEY (audio_id) REFERENCES audio(id) DEFERRABLE INITIALLY DEFERRED",
                ),
            ],
            "audio",
            "temp_import_audio",
            [
                # No statements generated for constraints that do not reference the audio table,
                # or for unique or primary key statements
                # Drop orphan statements first
                dedent(
                    """
                    DELETE FROM audiolist_audios AS fk_table
                    WHERE NOT EXISTS(
                        SELECT 1 FROM temp_import_audio AS r
                        WHERE r.id = fk_table.audio_id
                    );
                    """
                ),
                # Statements to drop example_check_constraint from audio and then add to temp_import_audio
                "ALTER TABLE audio DROP CONSTRAINT example_check_constraint;",
                "ALTER TABLE temp_import_audio ADD CONSTRAINT example_check_constraint CHECK"
                " (char_length(title) > 5);",
                # Statements to drop the fkey constraint which previously referenced audio, and
                # add it back referencing temp_import_audio
                "ALTER TABLE audiolist_audios DROP CONSTRAINT audiolist_audios_audio_id_fkey;",
                "ALTER TABLE audiolist_audios ADD CONSTRAINT audiolist_audios_audio_id_fkey FOREIGN KEY"
                " (audio_id) REFERENCES temp_import_audio(id) DEFERRABLE INITIALLY DEFERRED;",
            ],
        ),
    ],
)
def test_generate_constraints_for_table(
    all_constraints, table_name, temp_table_name, expected_alter_statements
):
    actual = generate_constraints_for_table.function(
        all_constraints, table_name, temp_table_name
    )
    assert actual == expected_alter_statements
