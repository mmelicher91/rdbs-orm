from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, select
from sqlalchemy import create_engine

mapper_registry = registry() # nutný prvek
Base = mapper_registry.generate_base() # nutný prvek

######################
#### CREATE TABLE ####
######################
# 2 Tabulky: test_stat a test_zar
# docs: https://docs.sqlalchemy.org/en/20/orm/quickstart.html

class TestStatus(Base): # název třídy (OOP)
    __tablename__ = "test_stat" # jméno tabulky ve SQL
    id_stat = Column(Integer, primary_key=True)  # sloupec PK
    stat_nazev = Column(String(16), nullable=False) # sloupec název = aktivní, rezervní
    
    spojka_stat = relationship("TestZar", back_populates="spojka_zar") # vazba na další tab
    
class TestZar(Base):
    __tablename__ = "test_zar"
    id_zar = Column(Integer, primary_key=True) # id +1
    zar_inv = Column(Integer) # 001
    zar_nazev = Column(String(128)) # jméno
    fk_stat = Column(Integer, ForeignKey("test_stat.id_stat")) # FK klíč do tabulky "test_stat" na sloupec id_stat
    
    spojka_zar = relationship("TestStatus", back_populates="spojka_stat") # spojka do druhé tab

# funkce se zavolá jen jednou; prvotní vytvoření v SQL přes python
def zaloz_db(engine):
    mapper_registry.metadata.create_all(engine) # nutný prvek
    print("Vytvořil jsem se")
       
# nastavení propojení do PostgeSQL; každá db trochu jiný zápis
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost/test", future=True) # future=true .. aktivuje se nová verze

# zaloz_db(engine) # prvotní založení db, pak zakomentovat

###########################
#### INSERT into TABLE ####
###########################
# jeden z možných postupů - více na https://docs.sqlalchemy.org/en/14/orm/session_basics.html

# vložení do tabulky "test_stat"
#with Session(engine) as session:
#    promenna1 = TestStatus(stat_nazev="V opravě")
#    promenna2 = TestStatus(stat_nazev="Zapůjčeno")
#    vkládání po částech:
#    session.add(promenna1)
#    session.add(promenna2)
#    session.commit() 
    
# vložení do tabulky "test_zar";
#with Session(engine) as session: # načte spojení
#    promenna1 = TestZar(zar_inv="003",zar_nazev="Pocitac_1",fk_stat="1") # pk se nedefinuje
#    promenna2 = TestZar(zar_inv="002", zar_nazev="Pocitac_2", fk_stat="2")
    # hromadné vkládání
#    session.add_all([promenna1, promenna2]) 
#    session.commit() # nutné pro uložení do tabulky

###########################
#### SELECT from TABLE ####
###########################

# https://docs.sqlalchemy.org/en/14/orm/queryguide.html
# 

session=Session(engine)

# obyč select z jedné tabulky a vypsání některých hodnot
vyber1 = select(TestZar).where(TestZar.zar_nazev=="Pocitac_1")
vysledek = session.execute(vyber1)

print("Obyčejný select s podmínkou where=='Pocitac_1'\n")
for objekt in vysledek.scalars():
    print(objekt.zar_nazev, objekt.zar_inv)

# select s joinem
vyber2 = select(TestZar,TestStatus).join(TestZar.spojka_zar).where(TestZar.zar_nazev=="Pocitac_1")
print("\n !!!! Select s Joinem")
for objekt in session.execute(vyber2):
    print(objekt.TestZar.zar_nazev, objekt.TestStatus.stat_nazev)

# dalsí způsob vytisknutí  
print("\n Tisk vyber3 --------------------") 
vyber3 = select(TestZar).join(TestZar.spojka_zar).where(TestZar.zar_inv == "2")
vysledek = session.scalars(vyber3).one()
print(f"VARS příkaz: {vars(vysledek)}")
print(vysledek.zar_nazev)

# další způsob vytisknutí
print("\n Tisk vyber4 --------------------")
vyber4 = select(TestZar, TestStatus).join(TestZar.spojka_zar).order_by(TestZar.id_zar)
for radek in session.execute(vyber4):
    print(f"{radek.TestZar.zar_nazev} {radek.TestStatus.stat_nazev}")

# filtrování přes druhou tabulku  
print("\n Tisk vyber5 --------------------")
vyber5 = select(TestZar).join(TestZar.spojka_zar).where(TestStatus.stat_nazev == "Zrušeno")
vysledek = session.scalars(vyber5).one()
print(vysledek.zar_nazev)