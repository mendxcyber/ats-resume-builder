# Apresentando o ATS Resume Builder

Um currículo adaptado pode manter os mesmos fatos e mudar a ordem em que eles aparecem. Foi essa ideia que orientou este gerador de PDFs em Python.

O projeto lê um perfil e uma vaga em JSON, escolhe uma área por regras simples e aplica o resumo e a ordem de experiências definidos pelo usuário. O resultado usa uma coluna, texto selecionável e títulos convencionais.

O código foi extraído do JobFlow Local para permitir uso independente, sem Docker ou API de IA. Os exemplos publicados são fictícios. Testes verificam preservação de informações, seleção do resumo e ordem das experiências.

Esta versão não garante aprovação em ATS nem compreende livremente todos os requisitos de um anúncio. Ela oferece uma base pequena e legível para estudar geração de documentos, separação entre dados e apresentação e validação de saídas PDF.

Confira o exemplo de execução no README e adapte os arquivos com informações verdadeiras.
