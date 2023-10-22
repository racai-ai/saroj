import unittest
from io import StringIO
from unittest.mock import patch, mock_open

# path is absolute to test easier the module inside the IDE
from WebServiceModules.EntityMapping.entityMapping_process import *


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
    def test_read_replacement_dictionary_empty_file(self, mock_open_file):
        # Mock an empty file
        mock_open_file.return_value = StringIO('')

        # Call the function
        result = read_replacement_dictionary('dummy_file.txt')

        # Assert the expected output
        expected_result = {}
        self.assertEqual(result, expected_result)

    @patch('builtins.open')
    def test_read_replacement_dictionary_invalid_line(self, mock_open_file):
        # Mock a file with an invalid line
        file_content = "PERSON\tJohn\n\nINVALID_LINE\nLOCATION\tNew York\n"
        mock_open_file.return_value = StringIO(file_content)

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
        mock_file_open.mapping_file = "mocked_file_path.txt"
        ner_id_and_potential_suffix = "#PER1"
        result = search_mapping_file(mock_file_open.mapping_file, ner_id_and_potential_suffix)
        self.assertEqual(result, "Andrei")

    @patch('builtins.open', new_callable=mock_open, read_data="Nicusor\t#PER1\tAndrei\nMaria\t#PER2\tIoana")
    def test_search_mapping_file_not_found(self, mock_file_open):
        mock_file_open.mapping_file = "mocked_file_path.txt"
        ner_id_and_potential_suffix = "#PER5"
        result = search_mapping_file(mock_file_open.mapping_file, ner_id_and_potential_suffix)
        self.assertEqual(result, '')


class TestProcessAlreadyMappedReplacement(unittest.TestCase):

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_process_already_mapped_replacement_single_token(self):
        replacement = "John"
        ner_inst = "I-PER"
        ner_id_and_potential_suffix = "#B-PER2"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual("_", result)

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_process_already_mapped_replacement_suffix_present(self):
        replacement = "Maria"
        ner_inst = "B-PER"
        ner_id_and_potential_suffix = "#PER6_ei"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Mariei")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_process_already_mapped_replacement_suffix_not_present(self):
        replacement = "Maria"
        ner_inst = "B-PER"
        ner_id_and_potential_suffix = "#PER5"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Maria")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 2)
    def test_process_already_mapped_replacement_multiple_tokens(self):
        replacement = "Adina Ionescu"
        ner_inst = "B-PER"
        ner_id_and_potential_suffix = "#PER_ei"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Adinei")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_process_already_mapped_replacement_multiple_tokens_singlere_replacement(self):
        replacement = "Adina Ionescu"
        ner_inst = "B-PER"
        ner_id_and_potential_suffix = "#PER_ei"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Adinei Ionescu")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 2)
    def test_process_already_mapped_replacement_four_tokens(self):
        replacement = "Adina Ionescu Papadag Bengescu"
        ner_inst = "I-PER"
        ner_id_and_potential_suffix = "#PER"
        result = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
        self.assertEqual(result, "Papadag")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_suffix_without_underscore(self):
        # Test when ner_id_and_potential_suffix does not contain underscores and "XXX" is not in replacement
        result = process_already_mapped_replacement("Sara Adamescu", "B-PER", "#PER2")
        self.assertEqual(result, "Sara Adamescu")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_condition_not_met(self):
        # Test when none of the conditions are met
        result = process_already_mapped_replacement("Maria", "B-LOC", "#LOC1")
        self.assertEqual(result, "Maria")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 2)
    def test_condition_singular_token_replacement_available(self):
        # Test when none of the conditions are met
        result = process_already_mapped_replacement("Maria", "B-PER", "#PER1")
        self.assertEqual(result, "Maria")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 4)
    def test_default_return_condition(self):
        # Test when none of the conditions are met
        result = process_already_mapped_replacement("Maria Elena Burlacu", "B-PER", "#PER1")
        self.assertEqual(result, "_")


class TestProcessEntityInstI(unittest.TestCase):

    @patch('WebServiceModules.EntityMapping.entityMapping_process.update_mapping_file')
    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    @patch('WebServiceModules.EntityMapping.entityMapping_process.old_rep', "Victor Ionescu Popescu")
    def test_process_entity_inst_I(self, mock_update_mapping_file):
        ner_id_and_potential_suffix = "#PER1"
        mapping_file = "mocked_file_path.txt"

        result = process_entity_inst_I(ner_id_and_potential_suffix, mapping_file)

        self.assertEqual("Popescu", result)
        mock_update_mapping_file.assert_called_with(mapping_file, ner_id_and_potential_suffix, "Popescu")


class TestProcessFemaleEntity(unittest.TestCase):

    @patch('WebServiceModules.EntityMapping.entityMapping_process.update_mapping_file')
    @patch('WebServiceModules.EntityMapping.entityMapping_process.hashtag_ner', return_value="#PER5")
    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_process_female_entity(self, mock_hashtag_ner, mock_update_mapping_file):
        # Define test data and initial dictionaries
        lemma = "Alina"
        ner_id_and_potential_suffix = "#PER5_ei"
        replacement_dict = {"PER": ["Maria Stancu", "Sara Adams"]}
        mapping_file = "mocked_file_path.txt"

        # Run the function under test
        result = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)

        # Assertions
        self.assertEqual("Mariei Stancu", result)
        mock_hashtag_ner.assert_called_with(ner_id_and_potential_suffix)
        mock_update_mapping_file.assert_called_with(mapping_file, "#PER5", "Maria Stancu")

    @patch('WebServiceModules.EntityMapping.entityMapping_process.update_mapping_file')
    @patch('WebServiceModules.EntityMapping.entityMapping_process.hashtag_ner', return_value="#PER88")
    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    def test_process_female_entity_suffix_missing(self, mock_hashtag_ner, mock_update_mapping_file):
        # Test when ner_id_and_potential_suffix does not contain a suffix
        lemma = "Mara"
        ner_id_and_potential_suffix = "#PER88"
        replacement_dict = {"PER": ["Amanda Smith", "Mary Johnson", "Sara Adams"]}
        mapping_file = "mocked_file_path.txt"

        result = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)

        expected_result = "Amanda Smith"
        self.assertEqual(result, expected_result)
        mock_hashtag_ner.assert_called_with(ner_id_and_potential_suffix)
        mock_update_mapping_file.assert_called_with(mapping_file, "#PER88", expected_result)

    @patch('WebServiceModules.EntityMapping.entityMapping_process.update_mapping_file')
    @patch('WebServiceModules.EntityMapping.entityMapping_process.hashtag_ner', return_value="#PER2")
    @patch('WebServiceModules.EntityMapping.entityMapping_process.counter_inst', 1)
    @patch('random.choice', return_value="Victor Smith")
    def test_process_female_entity_no_matching_replacement(self, mock_choice, mock_hashtag_ner,
                                                           mock_update_mapping_file):
        # Test when there's no matching replacement in the dictionary
        lemma = "Alina"
        ner_id_and_potential_suffix = "#PER2"
        replacement_dict = {"PER": ["Victor Smith", "Mihai Adams"]}
        mapping_file = "mocked_file_path.txt"

        result = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)

        expected_result = "Victor Smith"
        self.assertEqual(expected_result, result)
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
