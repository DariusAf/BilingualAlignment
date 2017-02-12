# -*- coding:utf-8 -*-
"""
This module was orinally coded by Mr Xavier CLERC before being completed by Matthieu
TOULEMONT.

We define a Trie class that enables the user to build a usual trie, a direct patricia trie,
and a reverse patricia trie.

@author Xavier CLERC and Matthieu TOULEMONT.
"""
import copy

def common_prefix_length(str1, str2):
    """
    Find the length of the common prefix between str1, and str2
    @author XC
    """
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
    """
    Find the common prefix of str1 and str2
    @author MT
    """
    m = common_prefix_length(str1, str2)
    return str1[:m]

def common_suffix_length(str1, str2):
    """
    Find the length of the common suffix between str1, and str2
    @author MT
    """
    if len(str1) > len(str2):
        return common_suffix_length(str2, str1)
    else:
        m = 0
        for i in range(len(str1)):
            if str1[len(str1) - 1 - i] == str2[len(str2) - 1 - i]:
                m += 1
            else:
                break
        return m

def common_suffix(str1, str2):
    """
    Find the common suffix between str1, and str2
    @author MT
    """
    m = common_suffix_length(str1, str2)
    return str1[len(str1)  - m :]

def find_common_prefix(adict,word):
    """
    Find common prefix of word and a list of keys in adict
    @author MT
    """
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

def find_common_suffix(adict, word):
    """
    Find common suffix between word and the list of keys from adict.
    @author MT
    """
    isin = 0
    mm = 0
    mkey = ''
    for key in adict:
        m = common_suffix_length(key, word)
        if m >= mm:
            isin = 1
            mm = m
            mkey = key
    if isin == 0:
        mkey = "None in children"
        mm = 0
    return mkey, mm

def symm_word(word):
    """
    Return the opposite word : 'life' -> 'efil'
    @author MT
    """
    m = len(word)
    tom= ""
    for i in range(m):
        tom += word[m-i-1]
    return tom

class Noeud:
    """
    Represent a node in the patricia trie. Holds a string and the information on wether
    the node marks the end of a word or not.
    @author XC
    """
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
    """
    Patricia Trie
    @author XC and MT
    """
    def __init__(self, kind):
        self.racine = Noeud("")
        self.feuilles = None
        self.type = kind #direct or inverse
    def ajoute(self, mot):
        """
        Add a word to the trie
        @author XC and MT
        """
        def ajoute_noeud_direct(noeud, suffixe, prefixe):
            """
            Useful if you want to build a direct patricia trie.
            """
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
                ajoute_noeud_direct(enfant, suffixe[1:], prefixe + lettre)
        def ajoute_noeud_inverse(noeud, prefixe, suffixe):
            """
            Useful if you want to build a reverse patricia trie
            """
            m = len(prefixe)
            if prefixe == "":
                noeud.present = True
                noeud.leaf = True
            else:
                lettre = prefixe[m-1]
                if lettre in noeud.enfants:
                    enfant = noeud.enfants[lettre]
                else:
                    enfant = Noeud(suffixe + lettre)
                    noeud.enfants[lettre] = enfant
                ajoute_noeud_inverse(enfant, prefixe[:m-1], suffixe + lettre)
        if self.type == 'direct':
            ajoute_noeud_direct(self.racine, mot, "")
        else:
            ajoute_noeud_inverse(self.racine, mot, "")
###
    def concatene_trie(self):
        """
        Useful if you to want to go from a usual trie to a patricia trie
        @author MT
        """
        def concatene(GP):
            """
            If two consecutive nodes only have one children we merge them into one.
            """
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
        """
        Check if a word is in the trie.
        @author XC
        """
        def trouve(noeud, suffixe):
            if suffixe == "":
                return noeud.present
            else:
                try:
                    (clef, split) = find_common_prefix(noeud.enfants, suffixe)
                    return trouve(noeud.enfants[clef[:split]], suffixe[split:])
                except KeyError:
                    return False

        if self.type == 'direct':
            return trouve(self.racine, mot)
        else:
            return trouve(self.racine, symm_word(mot))
###
    def trouve_feuilles(self):
        """
        Check if the node is a leaf and stores them inside self._feuilles.
        @author MT
        """
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
        """
        Find the longest stem for a word in the trie.
        @author MT
        """
        m = 0
        for i in range(len(mot)):
            if self.est_present(mot[:i]) and i >= min_stem_length:
                m = i
                break
        return m

###
    def est_present_prefixe(self, mot):
        """
        Check if a prefixe is in the trie.
        @author XC
        """
        def trouve(noeud, suffixe):
            if suffixe == "":
                return noeud.present, len(noeud.enfants) > 0
            else:
                try:
                    (clef, split) = find_common_prefix(noeud.enfants, suffixe)
                    return trouve(noeud.enfants[suffixe[:split]], suffixe[:split])
                except KeyError:
                    return False, False
        return trouve(self.racine, mot)
###
def lit_dictionnaire(nom_fichier):
    """
    Build a trie from a dictionnary :
    word1
    word2
    word3
    ...

    @author XC
    """
    res = Trie()
    with open(nom_fichier, "r") as fichier:
        for ligne in fichier:
            res.ajoute(ligne.strip("\n"))
    return res
###
def ecrit_dictionnaire(nom_fichier, trie):
    """
    Store the trie inside a .txt file under the form of a dictionnary.
    @author XC and MT
    """
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

def ecrit_segmentation(nom_fichier, se, itrie, dtrie):
    """
    Store the segmentation of each word in se in a .txt file for later analysis.
    @author XC and MT
    """
    with open(nom_fichier, "w") as fichier:
        for w in tuple(sorted(se)):
            p = dtrie.trouve_rad_max(w, 3)
            s = itrie.trouve_rad_max(w, 3)
            if p<= s:
                fichier.write(" {} | {} | {} \n \n".format(w[:p], w[p:s], w[s:]))
            else:
                fichier.write(" p :: {} | {} || s :: {} | {} \n \n".format(w[:p], w[p:],w[:s], w[s:]))
