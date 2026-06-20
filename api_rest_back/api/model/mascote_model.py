from enum import Enum

class Mascote():
    nome: str
    personalidade: PersonalidadeMascote
    tipo: TiposMascotes
    estado : EstadoMascote
    linguagem: TipoLinguagemMascote
    
    
class TiposMascotes(Enum):
    CACHORRO = "Cachorro"
    GATO = "Gato"
    COELHO = "Coelho"
    ELEFANTE = "Elefante"
    CORUJA = "Coruja"
    
class EstadoMascote(Enum):
    FELIZ = "Feliz"
    TRISTE = "Triste"
    CONFUSO = "Confuso"
    PREOCUPADO = "Preocupado"
    CALMO = "Calmo"
    
class TipoLinguagemMascote(Enum):
    FORMAL = "Formal"
    INFORMAL = "Informal"
    CASUAL = "Casual"
    
class PersonalidadeMascote(Enum):
    NERD = "Nerd"
    AVENTUREIRO = "Aventureiro"
    CALMO = "Calmo"
    DIVERTIDO = "Divertido"