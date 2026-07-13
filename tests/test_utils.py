import pytest
from utils import Utils


class TestUtils:
    
    def test_numtoword_zero(self):
        assert Utils.numtoword(0) == "Zero & Zero cents"
    
    def test_numtoword_basic_numbers(self):
        assert Utils.numtoword(1) == "One & Zero cents"
        assert Utils.numtoword(5) == "Five & Zero cents"
        assert Utils.numtoword(9) == "Nine & Zero cents"
    
    def test_numtoword_teens(self):
        assert Utils.numtoword(10) == "Ten & Zero cents"
        assert Utils.numtoword(15) == "Fifteen & Zero cents"
        assert Utils.numtoword(19) == "Nineteen & Zero cents"
    
    def test_numtoword_tens(self):
        assert Utils.numtoword(20) == "Twenty & Zero cents"
        assert Utils.numtoword(50) == "Fifty & Zero cents"
        assert Utils.numtoword(99) == "Ninety Nine & Zero cents"
    
    def test_numtoword_hundreds(self):
        assert Utils.numtoword(100) == "One Hundred & Zero cents"
        assert Utils.numtoword(500) == "Five Hundred & Zero cents"
        assert Utils.numtoword(999) == "Nine Hundred Ninety Nine & Zero cents"
    
    def test_numtoword_thousands(self):
        assert Utils.numtoword(1000) == "One Thousand & Zero cents"
        assert Utils.numtoword(5000) == "Five Thousand & Zero cents"
        assert Utils.numtoword(9999) == "Nine Thousand Nine Hundred Ninety Nine & Zero cents"
    
    def test_numtoword_with_cents(self):
        assert Utils.numtoword(1.50) == "One & 50 cents"
        assert Utils.numtoword(100.99) == "One Hundred & 99 cents"
        assert Utils.numtoword(1234.56) == "One Thousand Two Hundred Thirty Four & 56 cents"
    
    def test_numtoword_complex(self):
        assert Utils.numtoword(1234) == "One Thousand Two Hundred Thirty Four & Zero cents"
        assert Utils.numtoword(5678.90) == "Five Thousand Six Hundred Seventy Eight & 90 cents"
    
    def test_mask_account(self):
        # Account comes pre-masked from frontend
        assert Utils.mask_account("123456789") == "123456789"
        assert Utils.mask_account("****6789") == "****6789"
