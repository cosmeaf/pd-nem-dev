document.addEventListener('DOMContentLoaded', function() {
  const cpfInput = document.querySelector('input[name="cpf"]');
  
  cpfInput.addEventListener('input', function(e) {
      let cpf = e.target.value;
      
      // Remove todos os caracteres que não são números
      cpf = cpf.replace(/\D/g, '');
      
      // Limita o CPF a 11 dígitos
      cpf = cpf.substring(0, 11);

      // Formata como CPF (###.###.###-##)
      if (cpf.length > 9) {
          cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
      } else if (cpf.length > 6) {
          cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})/, "$1.$2.$3");
      } else if (cpf.length > 3) {
          cpf = cpf.replace(/(\d{3})(\d{3})/, "$1.$2");
      } else if (cpf.length > 0) {
          cpf = cpf.replace(/(\d{3})/, "$1");
      }
      
      e.target.value = cpf;
  });
});
