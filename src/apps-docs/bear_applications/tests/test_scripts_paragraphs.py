import os
import sys
from django.test import TestCase
from django.utils.lorem_ipsum import paragraphs
from testfixtures import log_capture, tempdir
from bear_applications.models import Application, ParagraphData

sys.path.insert(0, "../../scripts")
from paragraphs import add_para, list_para, para_filter, remove_para, replace_para, _save_para


class ParagraphsTestCase(TestCase):
    """
    Test the paragraphs.py script
    """

    fixtures = ["db.json"]

    def test_para_filter_for_application(self):
        """
        Test para_filter where a paragraph exists for an application
        """
        filter_q = para_filter(application="MATLAB")
        paras = ParagraphData.objects.filter(filter_q)
        self.assertEqual(filter_q.__len__(), 1)
        self.assertEqual(paras.count(), 2)
        self.assertEqual(paras[0].application.name, "MATLAB")
        self.assertIsNone(paras[0].version)
        self.assertEqual(paras[0].header, "first paragraph")
        self.assertEqual(paras[1].application.name, "MATLAB")
        self.assertIsNone(paras[1].version)
        self.assertEqual(paras[1].header, "second paragraph")

    def test_para_filter_for_version(self):
        """
        Test para_filter where a paragraph exists for a version
        """
        filter_q = para_filter(application="MATLAB", version="R2018b")
        paras = ParagraphData.objects.filter(filter_q)
        self.assertEqual(filter_q.__len__(), 1)
        self.assertEqual(paras.count(), 2)
        self.assertIsNone(paras[0].application)
        self.assertEqual(paras[0].version.version, "R2018b")
        self.assertEqual(paras[0].header, "a title")
        self.assertIsNone(paras[1].application)
        self.assertEqual(paras[1].version.version, "R2018b")
        self.assertEqual(paras[1].header, "some title")

    def test_para_filter_for_application_with_header(self):
        """
        Test para_filter where a paragraph exists for an application with header
        """
        filter_q = para_filter(application="MATLAB", header="second paragraph")
        paras = ParagraphData.objects.filter(filter_q)
        self.assertEqual(filter_q.__len__(), 2)
        self.assertEqual(paras.count(), 1)
        self.assertEqual(paras[0].application.name, "MATLAB")
        self.assertIsNone(paras[0].version)
        self.assertEqual(paras[0].header, "second paragraph")

    def test_para_filter_for_version_with_header(self):
        """
        Test para_filter where a paragraph exists for a version with header
        """
        filter_q = para_filter(application="MATLAB", version="R2018b", header="a title")
        paras = ParagraphData.objects.filter(filter_q)
        self.assertEqual(filter_q.__len__(), 2)
        self.assertEqual(paras.count(), 1)
        self.assertIsNone(paras[0].application)
        self.assertEqual(paras[0].version.version, "R2018b")
        self.assertEqual(paras[0].header, "a title")

    @log_capture()
    def test_remove_para_match(self, log):
        """
        Test remove_para where we match a paragraph
        """
        remove_para(application="MATLAB", header="first paragraph")
        log.check(("paragraphs", "INFO", "Deleted paragraph for MATLAB / None / first paragraph",))

    @log_capture()
    def test_remove_para_no_match(self, log):
        """
        Test remove_para where we don't match a paragraph
        """
        with self.assertRaises(SystemExit) as cm:
            remove_para(application="MATLAB", header="no paragraph")
        self.assertEqual(cm.exception.code, 1)
        log.check(("functions", "ERROR", "No paragraph matched the search"))

    @log_capture()
    def test_list_para_for_application(self, log):
        """
        Test para_list_parafilter where a paragraph exists for an application
        """
        list_para(application="MATLAB")
        log.check(
            ("paragraphs", "INFO", "Paragraph header: first paragraph"),
            ("paragraphs", "INFO", "Paragraph content:\nhere is some text"),
            ("paragraphs", "INFO", "==============================="),
            ("paragraphs", "INFO", "Paragraph header: second paragraph"),
            ("paragraphs", "INFO", "Paragraph content:\nhere is some text"),
            ("paragraphs", "INFO", "==============================="),
            ("paragraphs", "INFO", "Listed paragraph for to MATLAB / None"),
        )

    @log_capture()
    def test_list_para_for_version(self, log):
        """
        Test list_para where a paragraph exists for a version
        """
        list_para(application="MATLAB", version="R2018b")
        log.check(
            ("paragraphs", "INFO", "Paragraph header: a title"),
            ("paragraphs", "INFO", "Paragraph content:\nsome text"),
            ("paragraphs", "INFO", "==============================="),
            ("paragraphs", "INFO", "Paragraph header: some title"),
            ("paragraphs", "INFO", "Paragraph content:\nhere is some text"),
            ("paragraphs", "INFO", "==============================="),
            ("paragraphs", "INFO", "Listed paragraph for to MATLAB / R2018b"),
        )

    @log_capture()
    def test_list_para_for_application_with_header(self, log):
        """
        Test list_para where a paragraph exists for an application with header
        """
        list_para(application="MATLAB", header="second paragraph")
        log.check(
            ("paragraphs", "INFO", "Paragraph header: second paragraph"),
            ("paragraphs", "INFO", "Paragraph content:\nhere is some text"),
            ("paragraphs", "INFO", "==============================="),
            ("paragraphs", "INFO", "Listed paragraph for to MATLAB / None"),
        )

    @log_capture()
    def test_list_para_for_version_with_header(self, log):
        """
        Test list_para where a paragraph exists for a version with header
        """
        list_para(application="MATLAB", version="R2018b", header="a title")
        log.check(
            ("paragraphs", "INFO", "Paragraph header: a title"),
            ("paragraphs", "INFO", "Paragraph content:\nsome text"),
            ("paragraphs", "INFO", "==============================="),
            ("paragraphs", "INFO", "Listed paragraph for to MATLAB / R2018b"),
        )

    @tempdir()
    def test_save_para(self, dir):
        """
        Test save_para with a tmp file
        """
        para_obj = ParagraphData()
        para_obj.application = Application.objects.get(name="MATLAB")
        txt = "".join(paragraphs(2, common=False))
        dir.write("temp.txt", bytes(txt, encoding="UTF-8"))
        _save_para(para_obj, "info", os.path.join(dir.path, "temp.txt"))
        para = ParagraphData.objects.get(application__name="MATLAB", header="info")
        self.assertEqual(txt, para.content)

    @log_capture()
    def test_save_para_no_file(self, log):
        """
        Test save_para with no file
        """
        para_obj = ParagraphData()
        with self.assertRaises(SystemExit) as cm:
            _save_para(para_obj, "info", "temp.txt")
        self.assertEqual(cm.exception.code, 1)
        log.check(("functions", "ERROR", "Error ([Errno 2] No such file or directory: 'temp.txt') reading temp.txt"))

    @tempdir()
    @log_capture()
    def test_replace_para_match(self, log, dir):
        """
        Test replace_para
        """
        para_obj = ParagraphData()
        para_obj.application = Application.objects.get(name="MATLAB")
        txt = "".join(paragraphs(2, common=False))
        dir.write("temp.txt", bytes(txt, encoding="UTF-8"))
        replace_para(
            application="MATLAB",
            header="first paragraph",
            newheader="info",
            filename=os.path.join(dir.path, "temp.txt"),
        )
        para = ParagraphData.objects.get(application__name="MATLAB", header="info")
        self.assertEqual(txt, para.content)
        log.check(("paragraphs", "INFO", "Replaced paragraph for MATLAB / None / first paragraph"))

    @log_capture()
    def test_replace_para_no_match(self, log):
        """
        Test replace_para with no existing paragraph
        """
        with self.assertRaises(SystemExit) as cm:
            replace_para(application="MATLAB", header="info", filename="temp.txt")
        self.assertEqual(cm.exception.code, 1)
        log.check(("functions", "ERROR", "N no paragraph matched the search"))

    @tempdir()
    @log_capture()
    def test_add_para_application(self, log, dir):
        """
        Test add_para on application
        """
        txt = "".join(paragraphs(2, common=False))
        dir.write("temp.txt", bytes(txt, encoding="UTF-8"))
        add_para(
            application="MATLAB", header="new paragraph", filename=os.path.join(dir.path, "temp.txt"),
        )
        para = ParagraphData.objects.get(application__name="MATLAB", header="new paragraph")
        self.assertEqual(txt, para.content)
        log.check(("paragraphs", "INFO", "Added paragraph for MATLAB / None / new paragraph"))

    @tempdir()
    @log_capture()
    def test_add_para_version(self, log, dir):
        """
        Test add_para on version
        """
        txt = "".join(paragraphs(2, common=False))
        dir.write("temp.txt", bytes(txt, encoding="UTF-8"))
        add_para(
            application="MATLAB", version="R2018b", header="new paragraph", filename=os.path.join(dir.path, "temp.txt"),
        )
        para = ParagraphData.objects.get(
            version__application__name="MATLAB", version__version="R2018b", header="new paragraph"
        )
        self.assertEqual(txt, para.content)
        log.check(("paragraphs", "INFO", "Added paragraph for MATLAB / R2018b / new paragraph"))
