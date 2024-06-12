from bertalign import Bertalign

src = "Ciao"
tgt = "Hello"

aligner = Bertalign(src, tgt)
aligner.align_sents()

aligner.print_sents()