import io
import unittest
from extract_nodes import parse_nodes


class ParserTests(unittest.TestCase):
    def test_comments_case_and_repeated_labels_across_parts(self):
        rows = list(parse_nodes(io.StringIO('*pArT, name=A\n*NODE\n1,1D0,2\n** comment\n2,2,3,4\n*End Part\n*Part, name=B\n*Node\n1,0,0,0\n')))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], dict(part_name='A', node_id=1, x=1., y=2., z=0.))
        self.assertEqual(rows[-1]['part_name'], 'B')

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            list(parse_nodes(['*Part,name=A', '*Node', '1,0,0,0', '1,1,1,1']))

    def test_unsupported_features_rejected(self):
        for keyword in ('*Include,input=other.inp', '*System', '*Ngen'):
            with self.subTest(keyword=keyword), self.assertRaises(ValueError):
                list(parse_nodes([keyword]))

    def test_invalid_coordinates_rejected(self):
        with self.assertRaises(ValueError):
            list(parse_nodes(['*Part,name=A', '*Node', '1,nan,0,0']))


if __name__ == '__main__':
    unittest.main()
