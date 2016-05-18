import unittest
from mailmerge import *

class MailMergeTest(unittest.TestCase):

	def setUp(self):
		self.scalar = '$(DANCER) was in $(FILM). $(DANCER) is a dancer.'
		self.loop = "$FOR(DANCELIST,\"They danced the $(STEP) with $(DANCER)\")"
		self.combine = self.scalar + self.loop

		self.dict = {}
		self.dict['DANCER'] = 'Ginger Rogers'
		self.dict['FILM'] = 'The Martian'

		self.temp1 = {}
		self.temp1['STEP'] = 'Foxtrot'
		self.temp1['SCENE'] = '1'
		self.temp1['DANCER'] = 'Jimbo'

		self.temp2 = {}
		self.temp2['STEP'] = 'Rhumba'
		self.temp2['SCENE'] = '2'
		self.temp2['DANCER'] = 'Edgar'

		self.temp3 = [self.temp1, self.temp2]
		self.dict['DANCELIST'] = self.temp3

		self.scalar_result = 'Ginger Rogers was in The Martian. Ginger Rogers is a dancer.'
		self.loop_result = 'They danced the Foxtrot with Jimbo They danced the Rhumba with Edgar'

	# test fill_template
	def test_fill_template_with_empty_params(self):
		self.assertEqual(fill_template(), '')

	def test_fill_template_with_result_1(self):
		self.assertEqual(fill_template(self.scalar, self.dict), self.scalar_result)

	def test_fill_template_with_result_2(self):
		self.assertEqual(fill_template('$(DANCER)$(FILM)$(FILM)', self.dict), 'Ginger RogersThe MartianThe Martian')

	def test_fill_template_with_result_3(self):
		temp1 = {'STEP':'Foxtrot', 'DANCER': 'John'}
		temp2 = {'STEP':'Mexican', 'DANCER': 'The Police'}
		temp3 = {'DANCELIST': [temp1, temp2]}

		self.assertEqual(fill_template(self.loop, temp3), 'They danced the Foxtrot with John They danced the Mexican with The Police')

	def test_fill_template_with_result_4(self):
		temp1 = {}
		temp2 = {}
		temp3 = {'DANCELIST': [temp1, temp2]}
		self.assertEqual(fill_template("$FOR(DANCELIST,\"test\")", temp3), 'test test')

	def test_fill_template_with_result_5(self):
		temp1 = {'HELLO': 'Arvin'}
		temp2 = {'HELLO': 'Wanyu yin'}
		temp3 = {'abc123': [temp1, temp2]}
		self.assertEqual(fill_template("$FOR(abc123,\"hello$(HELLO)\")", temp3), 'helloArvin helloWanyu yin')

	def test_fill_template_with_result_6(self):
		self.assertEqual(fill_template(self.combine, self.dict), self.scalar_result + self.loop_result)

	def test_fill_template_with_longer_input(self):
		self.assertEqual(fill_template(self.combine + self.loop, self.dict), self.scalar_result + self.loop_result + self.loop_result)

	def test_fill_template_with_weird_macro_1(self):
		self.assertEqual(fill_template("($$$$$A)", {}), "(A)")

	def test_fill_template_with_weird_macro_2(self):
		self.assertEqual(fill_template("$($$$$$A)", {}), "(A)")

	def test_fill_template_with_error(self):
		with self.assertRaises(MacroNotDefined) as raises:
			fill_template("$FOR(abc123,\"hello$(HELLO)\")", {})
		self.assertEqual(str(raises.exception), "The macro: 'abc123' is not defined")

	# test is_scalar()
	def test_is_scalar_returns_true(self):
		self.assertTrue(is_scalar('(D'))

	def test_is_scalar_returns_false_when_pattern_not_matched1(self):
		self.assertFalse(is_scalar('('))

	def test_is_scalar_returns_false_when_pattern_not_matched2(self):
		self.assertFalse(is_scalar('F'))

	def test_is_scalar__when_openbracket_is_followed_by_nonalpha_returns_false(self):
		self.assertFalse(is_scalar('(?'))

	def test_is_scalar_returns_false_when_param_is_empty(self):
		self.assertFalse(is_scalar(''))

	def test_is_scalar_returns_false_when_no_param_is_given(self):
		self.assertFalse(is_scalar())

	# test is_loop()
	def test_is_loop_returns_true(self):
		self.assertTrue(is_loop('FOR(s??'))

	def test_is_loop_when_openbracket_is_followed_by_nonalpha_returns_false(self):
		self.assertFalse(is_loop('FOR( something'))

	def test_is_loop_returns_false_when_pattern_not_matched_1(self):
		self.assertFalse(is_loop('FOR('))

	def test_is_loop_returns_false_when_pattern_not_matched_2(self):
		self.assertFalse(is_loop('FORA'))
	
	def test_is_loop_returns_false__when_pattern_not_matched_3(self):
		self.assertFalse(is_loop('FOR'))
	
	def test_is_loop_returns_false__when_pattern_not_matched_4(self):
		self.assertFalse(is_loop('FO'))

	def test_is_loop_returns_false_with_empty_string(self):
		self.assertFalse(is_loop(''))

	def test_is_loop_returns_false_when_no_param_is_given(self):
		self.assertFalse(is_loop())

	# test translate scalar
	def test_translate_scalar(self):
		temp = {'fgh':'test'}
		self.assertEqual(translate_scalar('(fgh) ijk', temp), 'test ijk')

	def test_translate_scalar_with_error(self):
		with self.assertRaises(MacroNotDefined) as raises: 
			translate_scalar('(fgh) ijk', {})
		self.assertEqual(str(raises.exception), "The macro: 'fgh' is not defined")

	# test translate loop
	def test_translate_loop(self):
		self.assertEqual(translate_loop('They danced the (STEP) in scene (SCENE)', self.temp3), 'They danced the Foxtrot in scene 1 They danced the Rhumba in scene 2')

	def test_translate_loop_with_error(self):
		with self.assertRaises(MacroNotDefined) as raises:
			temp = {}
			translate_loop('They danced the (STEP)', [temp])
		self.assertEqual(str(raises.exception), "The macro: 'STEP' is not defined")

if __name__ == '__main__':
	unittest.main()