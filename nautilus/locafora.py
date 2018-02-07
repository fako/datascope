PRODUCT_TRANSLATIONS = {
    "verse knoflook - waanzinnig aroma": "knoflook, verse",
    "alouette aardappel van boerderij gaos": "aardappel, alouette",
    "10-zadenbol brood desem, van eigen graan (gesneden)": "brood, 10-zadenbol desem",
    "10-zadenbol  brood desem, van eigen graan (gesneden)": "brood, 10-zadenbol desem",
    "brood zonnelied 10 zaden bol, desem gesneden": "brood, 10-zadenbol desem",
    "afbak baguettes": "baguettes, afbak",
    "ambachtelijke ontbijtkoek": "ontbijtkoek, ambachtelijke",
    "bos verse platte peterselie": "peterselie, bos verse platte",
    "afbak breekbrood van eigen graan": "brood, afbak breekbrood",
    "pers sinaasappels navelina": "sinaasappels, pers, navelina",
    "trostomaat": "tomaat, tros",
    "zeeuwse zeewierburger - prolaterre": "zeewierburger, zeeuwse, prolaterre",
    "zonnelied vruchtenbol - gist": "brood, vruchtenbol, gist",
    "chioggia bieten": "bieten, chioggia",
    "crèmehoning - klaver en zo": "honing, crème",
    "gele uien": "uien, gele",
    "geraspte parmigiano reggiano": "parmigiano reggiano, geraspte",
    "gerookte spekblokjes": "spekblokjes, gerookte",
    "gewassen peen": "peen, gewassen",
    "groene pompoen": "pompoen, groene",
    "halfvolle melk van zuivelboerderij fam. de lange uit de weerribben": "melk, halfvolle",
    "koe mozzarella - castelli": "mozzarella, koe - castelli",
    "magere stooflappen": "stooflappen, magere",
    "oranje pompoen": "pompoen, oranje",
    "rode bieten": "bieten, rode",
    "rode eikenbladsla": "eikenbladsla, rode",
    "rode kool met appel verpakt": "kool, rode met appel verpakt",
    "rodelika winterpeen": "peen, winter (rodelika)",
    "runder rookworst": "rookworst, runder",
    "spelt speculaasjes": "speculaasjes, spelt",
    "topaz - appel voor fijnproevers": "appelen, topaz",
    "vers gerookte makreelfilet - meij": "makreelfilet, gerookt",
    "verse gember": "gember",
    "verse rode peper": "peper, rood",
    "volle melk - weerribben": "melk, volle",
    "volle yoghurt van klaas de lange uit nationaal park de weerribben": "yoghurt, volle",
    "witte kool van reggy": "kool, witte",
    "zonnelied brood volkoren - gist - gesneden": "brood, volkoren - gist - gesneden",
    "zonnelied noten rozijnenslof - desem": "brood, noten rozijnenslof - desem",
    "biolissimo cherry trostomaatjes": "tomaatjes, cherry tros",
    "elstar appels": "appels, elstar",
    "fries roggebrood": "roggebrood, fries",
    "groene of rode eikenbladsla van reggy - prachtige kroppen!": "sla, eikenblad, groene of rode",
    "halfvolle yoghurt weeribben": "yoghurt, halfvolle",
    "kleintje zonnelied brood - kasteeltje - gist": "brood, kasteeltje - gist",
    "little gem sla": "sla, little gem",
    "moro bloedsinaasappels": "bloedsinaasappels, moro",
    "paarse koolrabi": "koolrabi, paarse",
    "pitloze mix olijven": "olijven, pitloze mix",
    "punt paprika's": "paprika's, punt",
    "rode paprika": "paprika, rode",
    "zonnezaad brood volkoren - desem - gesneden": "brood, volkoren - desem - gesneden"
}


def get_product(title):
    # Clean input
    product = title.lower().strip()
    # Strip any prefix variants of "biologisch"
    if product.startswith("bio"):
        product = " ".join(product.split(" ")[1:]).strip()
    # Lookup product in translation table to see if their are better strings
    return PRODUCT_TRANSLATIONS.get(product, product)
