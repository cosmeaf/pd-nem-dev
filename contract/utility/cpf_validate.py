from validate_docbr import CPF

class CPFValidator:
    def __init__(self, cpf):
        self.cpf = cpf
        self.validator = CPF()

    def is_valid(self):
        """
        Verifica se o CPF é válido.
        """
        return self.validator.validate(self.cpf)

    def formatted_cpf(self):
        """
        Retorna o CPF formatado no padrão XXX.XXX.XXX-XX.
        """
        return self.validator.mask(self.cpf)
