from tests.utils import create_mock_audio


class TestAudio:
    @staticmethod
    def test_extension():
        single_file = create_mock_audio({"alt_files": None})
        assert single_file.extension == "mp3"
        alt_files = create_mock_audio()
        assert alt_files.extension == ["m4a"]
