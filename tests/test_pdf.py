import sys
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ats_resume import build_pdf, choose_track
from pypdf import PdfReader

class PdfTest(unittest.TestCase):
    def test_pdf_preserves_data_and_order(self):
        candidate=json.loads((ROOT/'examples/candidate.json').read_text(encoding='utf-8'))
        job=json.loads((ROOT/'examples/job.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'CV.pdf'
            build_pdf(job,candidate,target)
            reader=PdfReader(target)
            text=''.join(p.extract_text() for p in reader.pages)
            self.assertEqual(len(reader.pages),1)
            self.assertIn('pessoa@example.com',text)
            self.assertIn(candidate['resumos']['tecnologia'],text)
            self.assertLess(text.index('Empresa Exemplo A'),text.index('Empresa Exemplo B'))
            self.assertNotIn('Segurança Cibernética',text)
            self.assertNotIn('FIAP',text)
    def test_track_selection(self):
        self.assertEqual(choose_track('suporte tecnologia sistemas'),'tecnologia')
        self.assertEqual(choose_track('vendas comercial prospecção'),'comercial')

if __name__=='__main__':unittest.main()
