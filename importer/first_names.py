# frequent first names in german speaking clubs, to suggest the gender in the import (always shown as an estimate).
# Compiled by hand, extend as needed; names that are used for both (e.g. Kim, Toni) are left out on purpose.
# 2026-11-22: names of a real club list added (first names only, genders as told by Thomas; Chris and Robin as male).

MALE = """
aaron adam adrian albert albin alexander alfons alfred alois andre andreas anton armin arne arno arnold arthur
august axel bastian ben benedikt benjamin bernd bernhard bjoern bodo bruno carl carsten chris christian christoph
christopher claus clemens constantin damian daniel david denis dennis dieter dietmar dietrich dimitrios dirk
dominic dominik eduard egon elias emil eric erich erik ernst erwin eugen fabian felix ferdinand finn florian frank
franz friedhelm friedrich fritz georg gerd gerhard gernot gottfried gregor guenter guenther gustav hannes hans
harald hartmut heiko heiner heinrich heinz helmut henning henrik herbert hermann holger horst hubert hugo ingo
jakob jan jannik jens jeremias joachim jochen johann johannes jonas jonathan josef juergen julian julius justus kai
karl karsten kilian klaus konrad konstantin kurt lars leo leon leonard leonhard linus lorenz louis luca lucas
ludwig luis lukas lutz magnus malte manfred manuel marc marcel marco marcus mario mark markus martin mathias
matthias max maximilian michael moritz nico niklas niko nikolai nikolaus nils noah norbert olaf oliver oskar otto
pascal patrick paul peter philipp rainer ralf ralph reinhard reinhold rene richard robert robin roland rolf roman
rudolf ruediger samuel sebastian siegfried simon stefan steffen stephan sven theo theodor thomas thorsten tilo tim
timo tobias torsten udo ulrich uwe valentin veit viktor vincent volker walter werner wilhelm willfried willhelm
willi winfried wolfgang xaver yannick
"""

FEMALE = """
ada agnes alexandra alina amelia amelie andrea angela angelika anita anja anke anna anne annegret anneliese
annemarie annette annika antje antonia astrid barbara beate bettina bianca birgit brigitte britta carina carla
carmen carolin caroline charlotte christa christel christiane christina christine clara claudia cordula cornelia
dagmar daniela diana doris dorothea edith elena elfriede elisabeth elke ella ellen elsa emilia emily emma erika
erna eva evelyn franziska frieda friederike gabriele gerda gertrud gisela greta gudrun hanna hannah hannelore heidi
heike helene helga hildegard ida ilse ina ingeborg ingrid irene iris isabel isabell jana janina jasmin jennifer
jessica johanna josefine judith julia juliane jutta karin katharina kathrin katja katrin kerstin klara kristina
lara laura lea lena leni leonie lina linda lisa luisa luise lydia magdalena maja manuela mareike margarete margit
maria marianne marie marina marion marleen marlene marta martha martina maxima melanie mia michaela miriam monika
nadine nadja natalie nicole nina nora olga patricia paula petra pia ramona regina renate rita rosa rosemarie ruth
sabine sabrina sandra sara sarah silke silvia simone sofia sofie sonja sophia sophie stefanie stephanie susanne
svenja swantje tamara tanja theresa tina ulrike ursula ute valentina vanessa vera verena veronika viktoria waltraud
wiebke yvonne
"""


def name_set(text):
    return frozenset(text.split())


MALE_NAMES, FEMALE_NAMES = name_set(MALE), name_set(FEMALE)
