# Site du Kit Premier Stage

Le site est dans le dossier `docs/` pour être publié directement par GitHub Pages.

Site statique (HTML, CSS, JavaScript), sans outil de compilation. Il s'héberge tel quel sur GitHub Pages, Netlify, Vercel ou n'importe quel hébergeur.

## Pages
- `index.html` : l'accueil (présentation et raccourcis vers les autres pages)
- `contenu.html`, `methode.html`, `faq.html` : le contenu du kit, la méthode, les questions
- `acheter.html` : l'espace d'achat (prix, case de consentement, bouton de paiement)
- `mentions-legales.html`, `cgv.html`, `confidentialite.html` : les pages légales
- `style.css` : le style commun · `site.js` : prix, contact et bouton de paiement · `config.js` : les réglages
- `media/` : la vidéo de démonstration et son image d'attente

## À faire avant la mise en ligne

1. **Le prix, le lien de paiement et l'e-mail** : dans `config.js`.
   - `price` : le prix TTC affiché partout.
   - `checkoutUrl` : ton lien de paiement. Tant qu'il est vide, le bouton « Payer » affiche « Le paiement n'est pas encore activé ».
   - `contactEmail` : ton adresse de contact.
2. **Les champs surlignés en jaune** dans les trois pages légales : identité, statut, SIRET, adresse, TVA, hébergeur, prestataire de paiement, médiateur, dates.
3. **Le médiateur de la consommation** : l'adhésion est obligatoire pour vendre à des particuliers (par exemple CM2C ou Médicys, quelques dizaines d'euros par an).
4. **L'e-mail de confirmation** : il doit rappeler que le client a demandé l'accès immédiat et renoncé à son droit de rétractation (article L221-13 du Code de la consommation). La plupart des plateformes de paiement permettent d'ajouter ce texte.

## Paiement avec Payhip
Le site est configuré pour Payhip : crée ton produit sur payhip.com (en y déposant les 6 fichiers), copie le lien du produit (https://payhip.com/b/XXXX) et colle-le dans `checkoutUrl` dans `config.js`. Dans les réglages Payhip, ajoute au message de confirmation la phrase sur la renonciation au droit de rétractation.

## Autres solutions de paiement
- **Lemon Squeezy ou Gumroad** : le plus simple pour un produit numérique. Ils hébergent le fichier, envoient le lien de téléchargement et la facture, et gèrent la TVA européenne en tant que « vendeur officiel ». Une commission un peu plus élevée.
- **Stripe Payment Links** : commission plus faible, mais il faut gérer soi-même l'envoi du fichier et la TVA.

Dans tous les cas, colle le lien obtenu dans `checkoutUrl`.

## Mise en ligne rapide avec GitHub Pages
Dépôt GitHub → Settings → Pages → Build and deployment → Source : « Deploy from a branch », branche `claude/upbeat-allen-ymmm6g`, dossier `/docs`. L'adresse du site sera https://nathanfbrr.github.io/Nathan/. L'hébergeur GitHub est déjà indiqué dans les mentions légales.

## Bon à savoir
- Le site ne dépose aucun cookie et n'a pas d'outil de statistiques : pas besoin de bandeau cookies. Si tu ajoutes le pixel TikTok ou Google Analytics, il faudra un bandeau de consentement et mettre à jour `confidentialite.html`.
- Les polices viennent de Google Fonts. Pour être plus strict sur le RGPD, télécharge-les et héberge-les dans le dossier du site.
- Les pages légales sont des modèles sérieux, mais elles ne remplacent pas l'avis d'un juriste.
