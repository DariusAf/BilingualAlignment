# -*- coding:utf-8 -*-
import copy

def common_prefix_length(str1, str2):
    if len(str1) > len(str2):
        return common_prefix_length(str2, str1)
    else:
        m = 0
        for i in range(len(str1)):
            if str1[i] == str2[i]:
                m += 1
            else:
                break
        return m
def common_prefix(str1, str2):
     m = common_prefix_length(str1, str2)
     return str1[:m]

def find_common_prefix(adict,word):
    isin = 0
    mm = 0
    mkey = ''
    for key in adict:
        m = common_prefix_length(key, word)
        if m >= mm:
            isin = 1
            mm = m
            mkey = key
    if isin == 0:
        mkey = "None in children"
        mm = 0
    return mkey, mm


class Noeud:
    def __init__(self, mot):
        self.mot = mot
        self.present = False
        self.leaf = False
        self.enfants = {}
    def ident(self):
        if self.mot != "":
            return self.mot
        else:
            return "_"
###
class Trie:
    def __init__(self):
        self.racine = Noeud("")
        self.feuilles = None
    def ajoute(self, mot):
        def ajoute_noeud(noeud, suffixe, prefixe):
            if suffixe == "":
                noeud.present = True
                noeud.leaf = True
            else:
                lettre = suffixe[0]
                if lettre in noeud.enfants:
                    enfant = noeud.enfants[lettre]
                else:
                    enfant = Noeud(prefixe + lettre)
                    noeud.enfants[lettre] = enfant
                ajoute_noeud(enfant, suffixe[1:], prefixe + lettre)
        ajoute_noeud(self.racine, mot, "")
###
    def concatene_trie(self):
        def concatene(GP):
            if len(GP.enfants) != 0:
                Oncle = ""
                for (Pere, P) in GP.enfants.items():
                    Oncle = Pere
                    On = P
                    if len(P.enfants) == 1 and P.present == False:
                        for (Fils, F) in P.enfants.items():
                            Oncle = Pere + Fils
                            On = Noeud(Oncle)
                            On.present = F.present
                            On.leaf = F.leaf
                            On.enfants = copy.deepcopy(F.enfants)
                    if Oncle != Pere:
                        GP.enfants[Oncle] = On
                        del GP.enfants[Pere]
                    concatene(On)
        concatene(self.racine)
###
    def est_present(self, mot):
        def trouve(noeud, suffixe):
            if suffixe == "":
                return noeud.present
            else:
                try:
                    (clef, split) = find_common_prefix(noeud.enfants, suffixe)
                    return trouve(noeud.enfants[clef[:split]], suffixe[split:])
                except KeyError:
                    return False
        return trouve(self.racine, mot)
###
    def trouve_feuilles(self):
        if self.feuilles is None:
            self.feuilles = dict()
        def parcourt(noeud):
            for (nom, enfant) in noeud.enfants.items():
                if len(enfant.enfants) == 0:
                    if nom not in self.feuilles:
                        self.feuilles[nom] = 1
                    else:
                        self.feuilles[nom] += 1
                else:
                    parcourt(noeud.enfants[nom])
        parcourt(self.racine)
###
    def trouve_rad_max(self, mot, min_stem_length):
        m = 0
        for i in range(len(mot)):
            if self.est_present(mot[:i]) and i >= min_stem_length:
                m = i
                break
        return m

###
    def est_present_prefixe(self, mot):
        def trouve(noeud, suffixe):
            if suffixe == "":
                return noeud.present, len(noeud.enfants) > 0
            else:
                try:
                    (clef, split) = find_common_prefix(noeud.enfants, suffixe)
                    return trouve(noeud.enfants[suffixe[:split]], suffixe[split:])
                except KeyError:
                    return False, False
        return trouve(self.racine, mot)
###
def lit_dictionnaire(nom_fichier):
    res = Trie()
    with open(nom_fichier, "r") as fichier:
        for ligne in fichier:
            res.ajoute(ligne.strip("\n"))
    return res
###
def ecrit_dictionnaire(nom_fichier, trie):
    def parcourt(noeud, f):
        if noeud.present:
            shape = "(O)"
        else:
            shape = "o"
            f.write("  {} [shape={}];\n".format(noeud.ident(), shape))
        for (lettre, enfant) in noeud.enfants.items():
            f.write("  {} -> {} [label=\"{}\"];\n".format(noeud.ident(),
                                                enfant.ident(),
                                                    lettre))
            parcourt(enfant, f)
    with open(nom_fichier, "w") as fichier:
        fichier.write("digraph trie {")
        parcourt(trie.racine, fichier)
        fichier.write("}")
