import unittest
from paper2blog.agent import BlogGenerationAgent

class TestSectionSplitting(unittest.TestCase):
    def setUp(self):
        self.agent = BlogGenerationAgent()

    def test_variant_headers(self):
        text = '''
        Introduction
        This is intro

        2. Methodology
        Method section content

        Evaluation
        Results go here

        Discussion
        Final thoughts
        '''
        result = self.agent._split_text(text)
        print("\nFound sections:", result)  # Debug output
        self.assertEqual(len(result), 4)
        self.assertEqual(result['Introduction'], 'This is intro')
        self.assertEqual(result['Method'], 'Method section content')
        self.assertEqual(result['Experiments'], 'Results go here')
        self.assertEqual(result['Conclusion'], 'Final thoughts')

    def test_stop_sections(self):
        text = '''
        Abstract
        Content

        References
        Some citations
        '''
        result = self.agent._split_text(text)
        self.assertEqual(len(result), 1)
        self.assertIn('Abstract', result)

    def test_case_insensitivity(self):
        text = '''
        RELATED WORK
        Prior research

        APPENDIX
        Extra data
        '''
        result = self.agent._split_text(text)
        self.assertEqual(len(result), 1)
        self.assertIn('Related Work', result)

if __name__ == '__main__':
    unittest.main()
