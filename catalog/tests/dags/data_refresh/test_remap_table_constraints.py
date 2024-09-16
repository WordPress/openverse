from textwrap import dedent

import pytest

from data_refresh.remap_table_constraints import (
    ConstraintInfo,
    generate_constraints_for_table,
)


# Constraint that does not apply to or reference the table_name table
INAPPLICABLE_CONSTRAINT = ConstraintInfo(
    "image", "irrelevant_constraint", "CHECK (char_length(foo) = 5)"
)
# Foreign key constraint that does not apply to or reference the table_name table
INAPPLICABLE_FOREIGN_KEY_CONSTRAINT = ConstraintInfo(
    "imagelist_images",
    "imagelist_images_image_id_fkey",
    "FOREIGN KEY (image_id) REFERENCES image(id) DEFERRABLE INITIALLY DEFERRED",
)
# Primary key constraint; no alters should be generated
PRIMARY_KEY_CONSTRAINT = ConstraintInfo("audio", "audio_pkey", "PRIMARY KEY (id)")
# Unique constraint; no alters should be generated
UNIQUE_CONSTRAINT = ConstraintInfo("audio", "audio_url_key", "UNIQUE (url)")
# Constraint that applies to the table_name and should have alters generated
APPLICABLE_CONSTRAINT = ConstraintInfo(
    "audio",
    "example_check_constraint",
    "CHECK (char_length(title) > 5)",
)
# Foreign key constraint for which alters and drop_orphans should be generated
APPLICABLE_FOREIGN_KEY_CONSTRAINT = ConstraintInfo(
    "audiolist_audios",
    "audiolist_audios_audio_id_fkey",
    "FOREIGN KEY (audio_id) REFERENCES audio(id) DEFERRABLE INITIALLY DEFERRED",
)

EXPECTED_DROP_ORPHANS_STATEMENT = dedent(
    """
    DELETE FROM audiolist_audios AS fk_table
    WHERE NOT EXISTS(
        SELECT 1 FROM temp_import_audio AS r
        WHERE r.id = fk_table.audio_id
    );
    """
)

# Statements to drop example_check_constraint from audio and then add to temp_import_audio
EXPECTED_ALTER_TABLE_STATEMENTS = [
    "ALTER TABLE audio DROP CONSTRAINT example_check_constraint;",
    "ALTER TABLE temp_import_audio ADD CONSTRAINT example_check_constraint CHECK (char_length(title) > 5);",
]

# Statements to drop the fkey constraint which previously referenced audio, and
# add it back referencing temp_import_audio
EXPECTED_ALTER_TABLE_FOREIGN_KEY_STATEMENTS = [
    "ALTER TABLE audiolist_audios DROP CONSTRAINT audiolist_audios_audio_id_fkey;",
    "ALTER TABLE audiolist_audios ADD CONSTRAINT audiolist_audios_audio_id_fkey FOREIGN KEY"
    " (audio_id) REFERENCES temp_import_audio(id) DEFERRABLE INITIALLY DEFERRED;",
]


@pytest.mark.parametrize(
    "all_constraints, expected_alter_statements",
    [
        # No constraints
        ([], []),
        pytest.param([INAPPLICABLE_CONSTRAINT], [], id="inapplicable_constraint"),
        pytest.param(
            [INAPPLICABLE_FOREIGN_KEY_CONSTRAINT], [], id="inapplicable_fk_constraint"
        ),
        pytest.param(
            [PRIMARY_KEY_CONSTRAINT], [], id="pk_constraint_generates_no_alters"
        ),
        pytest.param(
            [UNIQUE_CONSTRAINT], [], id="unique_constraint_generates_no_alters"
        ),
        pytest.param(
            [APPLICABLE_CONSTRAINT],
            EXPECTED_ALTER_TABLE_STATEMENTS,
            id="applicable_constraint",
        ),
        pytest.param(
            [APPLICABLE_FOREIGN_KEY_CONSTRAINT],
            [
                # Drop orphans first
                EXPECTED_DROP_ORPHANS_STATEMENT,
                *EXPECTED_ALTER_TABLE_FOREIGN_KEY_STATEMENTS,
            ],
            id="applicable_foreign_key_constraint",
        ),
        pytest.param(
            [
                INAPPLICABLE_CONSTRAINT,
                INAPPLICABLE_FOREIGN_KEY_CONSTRAINT,
                PRIMARY_KEY_CONSTRAINT,
                UNIQUE_CONSTRAINT,
                APPLICABLE_CONSTRAINT,
                APPLICABLE_FOREIGN_KEY_CONSTRAINT,
            ],
            [
                # Drop orphans first
                EXPECTED_DROP_ORPHANS_STATEMENT,
                *EXPECTED_ALTER_TABLE_STATEMENTS,
                *EXPECTED_ALTER_TABLE_FOREIGN_KEY_STATEMENTS,
            ],
            id="correct_alter_table_order",
        ),
    ],
)
def test_generate_constraints_for_table(all_constraints, expected_alter_statements):
    actual = generate_constraints_for_table.function(
        all_constraints, "audio", "temp_import_audio"
    )
    assert actual == expected_alter_statements
