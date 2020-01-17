from storage import image


def test_init_includes_provider_in_output_files_string():
    image_store = image.ImageStore('test_provider')
    assert type(image_store._OUTPUT_FILE) == str
    assert 'test_provider' in image_store._OUTPUT_FILE


def test_create_tsv_row_returns_non_none_if_required_fields():
    image_store = image.ImageStore()
    test_image = image._Image(
            foreign_identifier=None,
            foreign_landing_url='https://image.org',
            image_url='https://image.org',
            thumbnail_url=None,
            width=None,
            height=None,
            filesize=None,
            license_='cc0',
            license_version='1.0',
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            tags=None,
            watermarked='f',
            provider=None,
            source=None,
    )
    actual_row = image_store._create_tsv_row(test_image)
    assert actual_row is not None


def test_create_tsv_row_returns_none_if_missing_foreign_landing_url():
    image_store = image.ImageStore()
    test_image = image._Image(
            foreign_identifier=None,
            foreign_landing_url=None,
            image_url='https://image.org',
            thumbnail_url=None,
            width=None,
            height=None,
            filesize=None,
            license_='cc0',
            license_version='1.0',
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            tags=None,
            watermarked='f',
            provider=None,
            source=None,
    )
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_returns_none_if_missing_license():
    image_store = image.ImageStore()
    test_image = image._Image(
            foreign_identifier=None,
            foreign_landing_url='https://image.org',
            image_url='https://image.org',
            thumbnail_url=None,
            width=None,
            height=None,
            filesize=None,
            license_=None,
            license_version='1.0',
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            tags=None,
            watermarked='f',
            provider=None,
            source=None,
    )
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_returns_none_if_missing_license_version():
    image_store = image.ImageStore()
    test_image = image._Image(
            foreign_identifier=None,
            foreign_landing_url='https://image.org',
            image_url='https://image.org',
            thumbnail_url=None,
            width=None,
            height=None,
            filesize=None,
            license_='cc0',
            license_version=None,
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            tags=None,
            watermarked='f',
            provider=None,
            source=None,
    )
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row


def test_create_tsv_row_returns_none_if_missing_image_url():
    image_store = image.ImageStore()
    test_image = image._Image(
            foreign_identifier=None,
            foreign_landing_url=None,
            image_url='https://image.org',
            thumbnail_url=None,
            width=None,
            height=None,
            filesize=None,
            license_='cc0',
            license_version='1.0',
            creator=None,
            creator_url=None,
            title=None,
            meta_data=None,
            tags=None,
            watermarked='f',
            provider=None,
            source=None,
    )
    expect_row = None
    actual_row = image_store._create_tsv_row(test_image)
    assert expect_row == actual_row
