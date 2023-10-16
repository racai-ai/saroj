import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch, mock_open

from entityMapping_process import *


class TestReadReplacementDictionary(unittest.TestCase):
    @patch('builtins.open')
    def test_read_replacement_dictionary(self, mo_open):
        # Mock the file content
        file_content = '''PER	Ioana Popescu
                          PER	Andrei Ionescu
                          PER	Maria
                          PER	Gheorghe
                          LOC	Bucuresti
                          LOC	Pitesti
                          ECLI	ECLI:RO:XXXX:XXXXX:XXXX
                          IBAN	RO00XXXXXXXXXXX'''

        mo_open.return_value = StringIO(file_content)

        # Call the function
        result = read_replacement_dictionary('dummy_file.txt')

        # Assert the expected output
        expected_result = {'ECLI': ['ECLI:RO:XXXX:XXXXX:XXXX'],
                           'IBAN': ['RO00XXXXXXXXXXX'],
                           'LOC': ['Bucuresti', 'Pitesti'],
                           'PER': ['Ioana Popescu', 'Andrei Ionescu', 'Maria', 'Gheorghe']}
        self.assertEqual(result, expected_result)

    @patch('builtins.open')
    def test_read_replacement_dictionary_empty_file(self, mock_open):
        # Mock an empty file
        mock_open.return_value = StringIO('')

        # Call the function
        result = read_replacement_dictionary('dummy_file.txt')

        # Assert the expected output
        expected_result = {}
        self.assertEqual(result, expected_result)

    @patch('builtins.open')
    def test_read_replacement_dictionary_invalid_line(self, mock_open):
        # Mock a file with an invalid line
        file_content = "PERSON\tJohn\n\nINVALID_LINE\nLOCATION\tNew York\n"
        mock_open.return_value = StringIO(file_content)

        # Call the function
        result = read_replacement_dictionary('dummy_file.txt')

        # Assert the expected output
        expected_result = {
            'PERSON': ['John'],
            'LOCATION': ['New York']
        }
        self.assertEqual(result, expected_result)


class TestUpdateMappingFile(unittest.TestCase):

    def setUp(self):
        # Create a temporary mapping file for testing
        self.mapping_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.mapping_file.write("entity1\tid1\n")
        self.mapping_file.write("entity2\tid2\n")
        self.mapping_file.write("entity3\tid3\textra3\n")
        self.mapping_file.close()

    def tearDown(self):
        # Remove the temporary mapping file after testing
        os.remove(self.mapping_file.name)

    def test_update_mapping_file(self):
        # Define the expected output after updating the mapping file
        expected_output = "entity1\tid1\n"
        expected_output += "entity2\tid2\textra2\n"
        expected_output += "entity3\tid3\textra3 replacement\n"

        # Call the function to update the mapping file
        update_mapping_file(self.mapping_file.name, "id3", "replacement")
        update_mapping_file(self.mapping_file.name, "id2", "extra2")

        # Read the updated mapping file
        with open(self.mapping_file.name, 'r') as file:
            actual_output = file.read()

        # Assert that the actual output matches the expected output
        self.assertEqual(actual_output, expected_output)


class TestSearchMappingFile(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data="Nicusor\t#PER1\tAndrei\nMaria\t#PER2\tIoana")
    def test_search_mapping_file_found(self, mock_file_open):
        mapping_file = "mocked_file_path.txt"
        ner_id_and_potential_suffix = "#PER1"
        result = search_mapping_file(mapping_file, ner_id_and_potential_suffix)
        self.assertEqual(result, "Andrei")

    @patch('builtins.open', new_callable=mock_open, read_data="Nicusor\t#PER1\tAndrei\nMaria\t#PER2\tIoana")
    def test_search_mapping_file_not_found(self, mock_file_open):
        mapping_file = "mocked_file_path.txt"
        ner_id_and_potential_suffix = "#PER5"
        result = search_mapping_file(mapping_file, ner_id_and_potential_suffix)
        self.assertIsNone(result)


class TestProcessAlreadyMappedReplacement(unittest.TestCase):

    def test_process_already_mapped_replacement_empty_replacement(self):
        replacement = ""
        ner_inst = "I-PER"
        ner_id_and_potential_suffix = "B-PER"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertIsNone(result)

    def test_process_already_mapped_replacement_single_token(self):
        replacement = "John"
        ner_inst = "I-PER"
        ner_id_and_potential_suffix = "B-PER"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertIsNone(result)

    def test_process_already_mapped_replacement_suffix_present(self):
        replacement = "Maria"
        ner_inst = "B-PER"
        ner_id_and_potential_suffix = "#PER6_ei"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Mariei")

    def test_process_already_mapped_replacement_suffix_not_present(self):
        replacement = "Maria"
        ner_inst = "B-PER"
        ner_id_and_potential_suffix = "#PER5"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Maria")

    def test_process_already_mapped_replacement_multiple_tokens(self):
        replacement = "Adina Ionescu"
        ner_inst = "B-PER"
        ner_id_and_potential_suffix = "#PER_ei"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Adinei")


class TestProcessEntityInstI(unittest.TestCase):

    @patch('entityMapping_process.used', {"PER": ["Victor Ionescu"]})
    @patch('entityMapping_process.update_mapping_file')
    @patch('entityMapping_process.count_i', 1)
    @patch('entityMapping_process.old_rep', "Victor")
    def test_process_entity_inst_I(self, mock_update_mapping_file, ):
        ner_id_and_potential_suffix = "#PER1"
        mapping_file = "mocked_file_path.txt"
        replacement_dict = {"PER": ["Grigore Ureche", "Maria Ionescu"]}

        result = process_entity_inst_I(ner_id_and_potential_suffix, mapping_file, replacement_dict)

        self.assertEqual("Ionescu", result)
        mock_update_mapping_file.assert_called_with(mapping_file, ner_id_and_potential_suffix, "Ionescu")
        self.assertEqual(replacement_dict, {"PER": ["Grigore Ureche", "Maria Ionescu"]})


class TestProcessFemaleEntity(unittest.TestCase):

    @patch('entityMapping_process.get_ner', return_value="PER")
    @patch('entityMapping_process.update_mapping_file')
    @patch('entityMapping_process.hashtag_ner', return_value="#PER5")
    def test_process_female_entity(self, mock_hashtag_ner, mock_update_mapping_file, mock_get_ner):
        # Define test data and initial dictionaries
        lemma = "Alina"
        ner_id_and_potential_suffix = "#PER5_ei"
        replacement_dict = {"PER": ["Maria Smith", "Maria Johnson", "Sara Adams"]}
        mapping_file = "mocked_file_path.txt"

        # Run the function under test
        result = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)

        # Assertions
        self.assertEqual("Mariei", result)
        mock_hashtag_ner.assert_called_with(ner_id_and_potential_suffix)
        mock_update_mapping_file.assert_called_with(mapping_file, "#PER5", "Mariei")

    @patch('entityMapping_process.get_ner', return_value="PER")
    @patch('entityMapping_process.update_mapping_file')
    @patch('entityMapping_process.hashtag_ner', return_value="#PER88")
    def test_process_female_entity_suffix_missing(self, mock_hashtag_ner, mock_update_mapping_file, mock_get_ner, ):
        # Test when ner_id_and_potential_suffix does not contain a suffix
        lemma = "Mara"
        ner_id_and_potential_suffix = "#PER88"
        replacement_dict = {"PER": ["Amanda Smith", "Mary Johnson", "Sara Adams"]}
        mapping_file = "mocked_file_path.txt"

        result = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)

        expected_result = "Amanda"
        self.assertEqual(result, expected_result)
        mock_hashtag_ner.assert_called_with(ner_id_and_potential_suffix)
        mock_update_mapping_file.assert_called_with(mapping_file, "#PER88", expected_result)

    @patch('entityMapping_process.get_ner', return_value="PER")
    @patch('entityMapping_process.update_mapping_file')
    @patch('entityMapping_process.hashtag_ner', return_value="#PER2")
    def test_process_female_entity_no_matching_replacement(self, mock_hashtag_ner, mock_update_mapping_file,
                                                           mock_get_ner):
        mock_randint = patch('random.randint')
        randint_mock = mock_randint.start()
        randint_mock.side_effect = [3]  # Returns values in the range [1, 3]

        # Test when there's no matching replacement in the dictionary
        lemma = "Alina"
        ner_id_and_potential_suffix = "#PER2"
        replacement_dict = {"PER": ["Victor Smith", "Mihai Adams"]}
        mapping_file = "mocked_file_path.txt"

        result = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)
        mock_randint.stop()
        expected_result = "XXX"
        self.assertEqual(result, expected_result)
        mock_hashtag_ner.assert_called_with(ner_id_and_potential_suffix)
        mock_update_mapping_file.assert_called_with(mapping_file, "#PER2", expected_result)


class TestPreprocessLine(unittest.TestCase):

    def test_valid_line(self):
        # Test a valid input line
        line = "1\tMariei\tB-PER\t#PER3_ei"
        expected_columns = ['1', 'Mariei', 'B-PER', '#PER3_ei']
        expected_result = (expected_columns, ('#PER3_ei', ('B-PER', 'Maria')))
        result = preprocess_line(line)
        self.assertEqual(result, expected_result)

    def test_empty_line(self):
        # Test an empty input line
        line = ""
        result = preprocess_line(line)
        self.assertEqual(result, (line, None))

    def test_comment_line(self):
        # Test a comment line
        line = "# This is a comment line"
        result = preprocess_line(line)
        self.assertEqual(result, (line, None))

    def test_void_ner(self):
        # Test a line with a VOID_NER
        line = "2\tJohn\tB-PER\t_"
        result = preprocess_line(line)
        self.assertEqual(result, (line, None))

    def test_line_with_suffix(self):
        # Test a line with a suffix in ner_id_and_potential_suffix
        line = "3\tSara\tB-PER\t#PER2_ei"
        expected_columns = ['3', 'Sara', 'B-PER', '#PER2_ei']
        expected_result = (expected_columns, ('#PER2_ei', ('B-PER', 'Sara')))
        result = preprocess_line(line)
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
