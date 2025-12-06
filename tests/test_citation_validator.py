import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from literature_autopilot.citation_validator import CitationValidator

class TestCitationValidator(unittest.TestCase):
    def setUp(self):
        self.extracted_data = [
            {
                "authors": ["Smith", "Doe"],
                "year": 2023,
                "title": "Paper A"
            },
            {
                "authors": ["Johnson"],
                "year": 2022,
                "title": "Paper B"
            }
        ]
        self.validator = CitationValidator(self.extracted_data)

    def test_valid_citation(self):
        text = "As shown by (Smith, 2023), this works."
        results = self.validator.validate_citations_in_text(text)
        self.assertEqual(len(results["valid"]), 1)
        self.assertEqual(results["valid"][0], ("Smith", "2023"))
        self.assertEqual(len(results["invalid"]), 0)

    def test_invalid_author(self):
        text = "However, (Brown, 2023) disagrees."
        results = self.validator.validate_citations_in_text(text)
        self.assertEqual(len(results["invalid"]), 1)
        self.assertEqual(results["invalid"][0], ("Brown", "2023"))

    def test_invalid_year(self):
        text = "Earlier work (Smith, 2020) suggests..."
        results = self.validator.validate_citations_in_text(text)
        self.assertEqual(len(results["invalid"]), 1)
        self.assertEqual(results["invalid"][0], ("Smith", "2020"))

    def test_multiple_citations(self):
        text = "Several studies (Smith, 2023) and (Johnson, 2022) confirm this."
        results = self.validator.validate_citations_in_text(text)
        self.assertEqual(len(results["valid"]), 2)

if __name__ == '__main__':
    unittest.main()
