<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>

    <xsl:variable name="edition-title" select="//presentation_data/presentation/title"/>
    <xsl:variable name="edition-subtitle" select="//presentation_data/presentation/subtitle"/>

    <!-- Variable pour stocker tous les projets uniques -->
    <xsl:key name="projects" match="//item" use="projet"/>

    <!-- Template principal qui gère la création de toutes les pages -->
    <xsl:template match="/">
        <xsl:call-template name="create-index"/>
        <xsl:call-template name="create-legal-mentions"/>
        <xsl:call-template name="create-about"/>
        <!-- pages projets -->
        <xsl:for-each select="//item[generate-id(.) = generate-id(key('projects', projet)[1])]">
            <xsl:sort select="projet"/>
            <xsl:call-template name="create-project-page">
                <xsl:with-param name="project" select="projet"/>
            </xsl:call-template>
        </xsl:for-each>
        <!-- pages œuvres, sources, fragments -->
        <xsl:for-each select="//item">
            <xsl:choose>
                <xsl:when test="nature = 'Oeuvre' and not(frag)">
                    <xsl:call-template name="create-work-page"/>
                </xsl:when>
                <xsl:when test="nature = 'Source'">
                    <xsl:call-template name="create-source-page"/>
                </xsl:when>
                <xsl:when test="nature = 'Fragment'">
                    <xsl:call-template name="create-frag-page"/>
                </xsl:when>
            </xsl:choose>
        </xsl:for-each>
    </xsl:template>

    <!-- Template pour générer le <head> commun -->
    <xsl:template name="common-head">
        <xsl:param name="page-path" select="''"/>
        <head>
            <meta charset="UTF-8"/>
            <title>CMBV - <xsl:value-of select="$edition-title"/></title>
            <link rel="stylesheet" type="text/css" href="{$page-path}statics/css/styles.css"/>
            <script type="text/javascript" src="{$page-path}statics/js/main.js"></script>
            <script type="text/javascript" src="{$page-path}statics/js/logo.js"></script>
        </head>
    </xsl:template>

    <!-- Template pour générer le header commun -->
    <xsl:template name="common-header">
        <xsl:param name="page-path" select="''"/>
        <header>
            <xsl:call-template name="cmbv-logo"/>
            <div class="header-content">
                <h1><a href="{$page-path}index.html"><xsl:value-of select="$edition-title"/></a></h1>
                <h2><xsl:value-of select="$edition-subtitle"/></h2>
            </div>
        </header>
    </xsl:template>

    <!-- Template pour générer le bandeau -->
    <xsl:template name="common-bandeau">
        <xsl:param name="page-path" select="''"/>
        <figure class="bandeau-box">
            <img class="bandeau" src="{$page-path}statics/img/recherche-cmbv-accueil.jpg"/>
        </figure>
    </xsl:template>

    <!-- Template pour générer le footer commun -->
    <xsl:template name="common-footer">
        <xsl:param name="page-path" select="''"/>
        <footer>
            <p><a href="{$page-path}legal_mentions.html">Mentions légales</a></p>
            <p><a href="{$page-path}about.html">À propos</a></p>
            <p>© Centre de Musique Baroque de Versailles - Base de données PHILIDOR4</p>
            <p class="smaller">Faire rayonner la musique française des XVIIe et XVIIIe siècles</p>
        </footer>
        <a class="retour-haut" href="#"></a>
        <a class="rayon" href="https://philidor4.cmbv.fr" target="_blank">
            <div class="rayon-text"><p>PHILIDOR4</p></div>
        </a>
    </xsl:template>

    <!-- Template refactorisé pour la page d'accueil -->
    <xsl:template name="create-index">
        <xsl:result-document href="output/index.html" method="html">
            <html>
                <xsl:call-template name="common-head">
                    <xsl:with-param name="page-path" select="''"/>
                </xsl:call-template>
                <body>
                    <xsl:call-template name="common-header">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                    
                    <xsl:call-template name="common-bandeau">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                    
                    <main>
                        <div class="main-content">
                            <section class="white-box">
                                <xsl:value-of select="//presentation_data/presentation/content"/>
                            </section>
                            <section class="blue-box">
                                <h3>Catalogues d'auteur</h3>
                                <p>Sélectionnez un auteur pour voir les œuvres associées :</p>
                                
                                <ul class="project-list">
                                    <xsl:for-each select="//item[generate-id(.) = generate-id(key('projects', projet)[1])]">
                                        <xsl:sort select="//projects_data//project[@id = current()/projet]/@name"/>
                                        <li>
                                            <a href="projects/{translate(projet, ' ', '_')}.html">
                                                <xsl:value-of select="//projects_data//project[@id = current()/projet]/@name"/>
                                            </a>
                                            <span class="work-count">
                                                (<xsl:value-of select="count(//item[projet = current()/projet])"/> œuvres)
                                            </span>
                                        </li>
                                    </xsl:for-each>
                                </ul>
                            </section>
                        </div>
                    </main>
                    
                    <xsl:call-template name="common-footer">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                </body>
            </html>
        </xsl:result-document>
    </xsl:template>

    <!-- Template refactorisé pour les mentions légales -->
    <xsl:template name="create-legal-mentions">
        <xsl:result-document href="output/legal_mentions.html" method="html">
            <html>
                <xsl:call-template name="common-head">
                    <xsl:with-param name="page-path" select="''"/>
                </xsl:call-template>
                <body>
                    <xsl:call-template name="common-header">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                    
                    <xsl:call-template name="common-bandeau">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                    
                    <main>
                        <section class="white-box">
                            <xsl:value-of select="//legal_mentions_data/legal_mentions/content"/>
                        </section>
                    </main>
                    
                    <xsl:call-template name="common-footer">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                </body>
            </html>
        </xsl:result-document>
    </xsl:template>

    <!-- Template pour la page "à propos" -->
    <xsl:template name="create-about">
        <xsl:result-document href="output/about.html" method="html">
            <html>
                <xsl:call-template name="common-head">
                    <xsl:with-param name="page-path" select="''"/>
                </xsl:call-template>
                <body>
                    <xsl:call-template name="common-header">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                    
                    <xsl:call-template name="common-bandeau">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                    
                    <main>
                        <section class="white-box">
                            <xsl:value-of select="//about_data/about/content"/>
                        </section>
                    </main>
                    
                    <xsl:call-template name="common-footer">
                        <xsl:with-param name="page-path" select="''"/>
                    </xsl:call-template>
                </body>
            </html>
        </xsl:result-document>
    </xsl:template>

    <!-- Template pour la page de presentation de chaque projet -->
    <xsl:template name="create-project-page">
        <xsl:param name="project"/>

        <xsl:result-document href="output/projects/{translate($project, ' ', '_')}.html" method="html">
            <html>
                <xsl:call-template name="common-head">
                    <xsl:with-param name="page-path" select="'../'"/>
                </xsl:call-template>
                <body>
                    <xsl:call-template name="common-header">
                        <xsl:with-param name="page-path" select="'../'"/>
                    </xsl:call-template>

                    <xsl:call-template name="common-bandeau">
                        <xsl:with-param name="page-path" select="'../'"/>
                    </xsl:call-template>

                    <main class="main-content">
                        <section class="white-box">

                            <!-- Variables locales -->
                            <xsl:variable name="project-sources" select="//item[projet = $project and nature = 'Source']"/>
                            <xsl:variable name="project-oeuvres" select="//item[projet = $project and nature = 'Oeuvre' and not(frag)]"/>

                            <!-- Titre principal -->
                            <h2 id="project-title">
                                <xsl:value-of select="//projects_data//project[@id = current()/projet]/@name"/>
                            </h2>

                            <!-- Aperçu éditorial -->
                            <div class="preview-box">
                                <xsl:value-of select="//projects_data//project[@id = current()/projet]/preview/node()"/>
                                <p><a class="btn" href="#full-description">Lire la suite</a></p>
                            </div>

                            <!-- Catalogue des recueils -->
                            <xsl:if test="count($project-sources) &gt; 0">
                                <div class="recueil-content">
                                    <h3 id="recueil-section">Catalogue des recueils</h3>
                                    <p>Sélectionnez un recueil pour voir sa notice</p>
                                    <ul>
                                        <xsl:for-each select="$project-sources">
                                            <xsl:sort select="srce_code"/>
                                            <li>
                                                <a href="../sources/{numero}.html">
                                                    <xsl:choose>
                                                        <xsl:when test="titre_cle_sre">
                                                            <xsl:value-of select="titre_cle_sre"/>
                                                        </xsl:when>
                                                        <xsl:when test="titre_cle">
                                                            <xsl:value-of select="titre_cle"/>
                                                        </xsl:when>
                                                        <xsl:when test="notice_bibl">
                                                            <xsl:call-template name="format-notice-ligne">
                                                                <xsl:with-param name="texte" select="notice_bibl"/>
                                                            </xsl:call-template>
                                                        </xsl:when>
                                                        <xsl:when test="srce_notes">
                                                            <xsl:call-template name="format-notice-ligne">
                                                                <xsl:with-param name="texte" select="srce_notes"/>
                                                            </xsl:call-template>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <em>Titre non spécifié</em>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </a>
                                            </li>
                                        </xsl:for-each>
                                    </ul>
                                </div>
                            </xsl:if>

                            <!-- Catalogue des œuvres -->
                            <div class="work-list">
                                <h3 id="oeuvre-section">Catalogue des œuvres</h3>
                                <p>Sélectionnez une œuvre pour voir sa notice</p>
                                <ul>
                                    <xsl:for-each select="$project-oeuvres">
                                        <xsl:sort select="srce_code"/>
                                        <li>
                                            <a href="../works/{numero}.html">
                                                <xsl:choose>
                                                    <xsl:when test="oeuvre != ''">
                                                        <xsl:call-template name="format-notice-ligne">
                                                            <xsl:with-param name="texte" select="oeuvre"/>
                                                        </xsl:call-template>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <em>Titre non spécifié</em>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </a>
                                            <xsl:if test="effectif"> (<xsl:value-of select="effectif"/>) </xsl:if>
                                        </li>
                                    </xsl:for-each>
                                </ul>
                            </div>

                            <!-- Description longue -->
                            <div class="project-description">
                                <h3 id="full-description">Description du projet : 
                                    <xsl:value-of select="//projects_data//project[@id = current()/projet]/@name"/>
                                </h3>
                                <xsl:value-of select="//projects_data//project[@id = current()/projet]/description_html/node()"/>
                            </div>
                        </section>

                        <!-- Sommaire -->
                        <section class="blue-box">
                            <h3>Sommaire de la page</h3>
                            <ul>
                                <li><a href="#project-title"><xsl:value-of select="//projects_data//project[@id = current()/projet]/@name"/></a></li>
                                <li><a href="#recueil-section">Catalogue des recueils</a></li>
                                <li><a href="#oeuvre-section">Catalogue des œuvres</a></li>
                            </ul>
                        </section>
                    </main>

                    <xsl:call-template name="common-footer">
                        <xsl:with-param name="page-path" select="'../'"/>
                    </xsl:call-template>
                </body>
            </html>
        </xsl:result-document>
    </xsl:template>

    <xsl:template name="create-source-page">
        <xsl:if test="string-length(normalize-space(numero)) > 0">
            <xsl:result-document href="output/sources/{numero}.html" method="html">
                <html>
                    <xsl:call-template name="common-head">
                        <xsl:with-param name="page-path" select="'../'"/>
                    </xsl:call-template>
                    <body>
                        <xsl:call-template name="common-header">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>
                        <xsl:call-template name="common-bandeau">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>

                        <main>
                            <article class="work-details">
                                <xsl:call-template name="notice-num"/>
                                <h2>
                                    <xsl:choose>
                                        <xsl:when test="titre_cle_sre != ''">
                                            <xsl:value-of select="titre_cle_sre"/>
                                        </xsl:when>
                                        <xsl:when test="titre_cle != ''">
                                            <xsl:value-of select="titre_cle"/>
                                        </xsl:when>
                                        <xsl:when test="notice_bibl">
                                            <xsl:call-template name="format-notice-ligne">
                                                <xsl:with-param name="texte" select="notice_bibl"/>
                                            </xsl:call-template>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <em>Titre non spécifié</em>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </h2>
                                <xsl:call-template name="main-informations"/>
                            </article>
                            <xsl:call-template name="other-informations"/>
                        </main>

                        <xsl:call-template name="common-footer">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>
                    </body>
                </html>
            </xsl:result-document>
        </xsl:if>
    </xsl:template>

    <xsl:template name="create-work-page">
        <xsl:if test="string-length(normalize-space(numero)) > 0">
            <xsl:result-document href="output/works/{numero}.html" method="html">
                <html>
                    <xsl:call-template name="common-head">
                        <xsl:with-param name="page-path" select="'../'"/>
                    </xsl:call-template>
                    <body>
                        <xsl:call-template name="common-header">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>
                        <xsl:call-template name="common-bandeau">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>

                        <main>
                            <article class="work-details">
                                <xsl:call-template name="notice-num"/>
                                <h2>
                                    <xsl:choose>
                                        <xsl:when test="oeuvre != ''">
                                            <xsl:value-of select="oeuvre"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <em>Titre non spécifié</em>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </h2>
                                <xsl:call-template name="main-informations"/>
                            </article>
                            <xsl:call-template name="other-informations"/>
                            <xsl:call-template name="liste-fragments-oeuvre"/>
                        </main>

                        <xsl:call-template name="common-footer">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>
                    </body>
                </html>
            </xsl:result-document>
        </xsl:if>
    </xsl:template>

    <!-- Template pour les pages des fragments -->
    <xsl:template name="create-frag-page">
        <xsl:if test="string-length(normalize-space(numero)) > 0">
            <xsl:result-document href="output/fragments/{numero}.html" method="html">
                <html>
                    <xsl:call-template name="common-head">
                        <xsl:with-param name="page-path" select="'../'"/>
                    </xsl:call-template>
                    <body>
                        <xsl:call-template name="common-header">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>
                        <xsl:call-template name="common-bandeau">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>

                        <main>
                            <article class="work-details">
                                <xsl:call-template name="notice-num"/>
                                <h2>
                                    <xsl:choose>
                                        <xsl:when test="frag != ''">
                                            <xsl:value-of select="frag"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <em>Titre non spécifié</em>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </h2>
                                <xsl:call-template name="main-informations"/>
                            </article>
                            <xsl:call-template name="other-informations"/>
                            <xsl:call-template name="oeuvre-parente-fragment"/>
                        </main>

                        <xsl:call-template name="common-footer">
                            <xsl:with-param name="page-path" select="'../'"/>
                        </xsl:call-template>
                    </body>
                </html>
            </xsl:result-document>
        </xsl:if>
    </xsl:template>

    <xsl:template name="notice-num">
        <div class="notice-num">
            <p class="num">
                <strong>
                    <xsl:if test="nature">
                        <xsl:value-of select="nature"/>
                    </xsl:if>
                    <xsl:if test="numero">
                        <span>, notice n°</span>
                        <xsl:value-of select="numero"/>
                    </xsl:if>
                </strong>
            </p>
            
            <xsl:if test="num_orig">
                <p class="num-orig">
                    <strong>Numéro d'origine (JLB ou EZPUBLISH) : </strong>
                    <span><xsl:value-of select="num_orig"/></span>
                </p>
            </xsl:if>
        </div>
    </xsl:template>

    <xsl:template name="main-informations">

            <div class="main-informations">
            
                <!-- Numéro et informations de base -->            
                <xsl:if test="type_contenu">
                <div class="field">
                    <strong>Type de contenu : </strong>
                    <span><xsl:value-of select="type_contenu"/></span>
                </div>
                </xsl:if>
                
                <xsl:if test="projet">
                <div class="field">
                    <strong>Projet : </strong>
                    <a href="../projects/{translate(projet, ' ', '_')}.html"><xsl:value-of select="//projects_data//project[@id = current()/projet]/@name"/></a>
                </div>
                </xsl:if>

                <!-- Personnes et fonctions avec pagination -->
                <xsl:if test="nomsFonctions">
                <div class="field work-text">
                    <strong>Personnes ayant un rapport avec l'oeuvre : </strong>
                    <xsl:choose>
                        <xsl:when test="count(nomsFonctions/item) > 7">
                            <!-- Container pour la pagination -->
                            <div class="pagination-container" data-total-items="{count(nomsFonctions/item)}">
                                <ul class="paginated-list">
                                    <xsl:for-each select="nomsFonctions/item">
                                        <li data-page="{ceiling(position() div 7)}">
                                            <xsl:value-of select="@key"/> - <xsl:value-of select="."/>
                                        </li>
                                    </xsl:for-each>
                                </ul>
                                <!-- Contrôles de pagination -->
                                <div class="pagination-controls">
                                    <button class="pagination-btn" data-action="prev">← Précédent</button>
                                    <span class="pagination-info">
                                        Page <span class="current-page">1</span> sur <span class="total-pages"><xsl:value-of select="ceiling(count(nomsFonctions/item) div 7)"/></span>
                                    </span>
                                    <button class="pagination-btn" data-action="next">Suivant →</button>
                                </div>
                            </div>
                        </xsl:when>
                        <xsl:otherwise>
                            <!-- Liste normale si 7 éléments ou moins -->
                            <ul>
                                <xsl:for-each select="nomsFonctions/item">
                                    <li><xsl:value-of select="@key"/> - <xsl:value-of select="."/></li>
                                </xsl:for-each>
                            </ul>
                        </xsl:otherwise>
                    </xsl:choose>
                </div>
                </xsl:if>

                <!-- Genres -->
                <div class="field">
                <strong>Genre musical : </strong>
                <xsl:choose>
                    <xsl:when test="genre_musical">
                        <span><xsl:value-of select="genre_musical"/></span>
                    </xsl:when>
                    <xsl:otherwise>
                        <span>Non renseigné</span>
                    </xsl:otherwise>
                </xsl:choose>
                </div>

                <div class="field">
                <strong>Genre du texte : </strong>
                <xsl:choose>
                    <xsl:when test="genre_texte">
                        <span><xsl:value-of select="genre_texte"/></span>
                    </xsl:when>
                    <xsl:otherwise>
                        <span>Non renseigné</span>
                    </xsl:otherwise>
                </xsl:choose>
                </div>

                <!-- Cotes -->
                <xsl:if test="cote_CMBV">
                <div class="field">
                    <strong>Cote CMBV : </strong>
                    <span><xsl:value-of select="cote_CMBV"/></span>
                </div>
                </xsl:if>

            </div>

    </xsl:template>

    <xsl:template name="other-informations">
        
        <!-- 1. Incipits -->
        <xsl:call-template name="incipits-section"/>
        
        <!-- 2. Effectif et instrumentation -->
        <xsl:call-template name="effectif-section"/>
        
        <!-- 3. Sources -->
        <xsl:call-template name="sources-section"/>
        
        <!-- 4. Informations textuelles -->
        <xsl:call-template name="informations-textuelles-section"/>
        
        <!-- 5. Références & mentions -->
        <xsl:call-template name="references-section"/>
        
        <!-- 6. Production scénique -->
        <xsl:call-template name="production-scenique-section"/>
        
        <!-- 7. Dates & lieux -->
        <xsl:call-template name="dates-lieux-section"/>
        
        <!-- 8. Liturgie -->
        <xsl:call-template name="liturgie-section"/>
        
        <!-- 9. Personnages, rôles, noms -->
        <xsl:call-template name="roles-personnages-section"/>
        
        <!-- 10. Notes et attributions -->
        <xsl:call-template name="notes-attributions-section"/>
        
        <!-- 11. Responsable de la saisie -->
        <xsl:call-template name="auteur-saisie-section"/>
        
    </xsl:template>

    <!-- 1. Section Incipits -->
    <xsl:template name="incipits-section">
        <xsl:if test="inc_fr or inc_lat or inc_mus">
            <xsl:variable name="incipitContent">
                <xsl:if test="inc_fr">
                    <div class="field">
                        <strong>Incipit français : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="inc_fr"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>

                <xsl:if test="inc_lat">
                    <div class="field">
                        <strong>Incipit latin : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="inc_lat"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>

                <xsl:if test="inc_mus">
                    <div class="field">
                        <strong>Incipit musical : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="inc_mus"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Incipit'"/>
                <xsl:with-param name="content" select="$incipitContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 2. Section Effectif et instrumentation -->
    <xsl:template name="effectif-section">
        <xsl:if test="effectif or effectif_not or instr">
            <xsl:variable name="effectContent">
                <div class="field">
                    <strong>Effectif musical : </strong>
                    <xsl:choose>
                        <xsl:when test="effectif">
                            <span><xsl:value-of select="effectif"/></span>
                        </xsl:when>
                        <xsl:otherwise>
                            <span>Non renseigné</span>
                        </xsl:otherwise>
                    </xsl:choose>
                </div>
                
                <xsl:if test="effectif_not">
                    <div class="field">
                        <strong>Note sur l'effectif : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="effectif_not"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <div class="field">
                    <strong>Instrumentation : </strong>
                    <xsl:choose>
                        <xsl:when test="instr">
                            <span><xsl:value-of select="instr"/></span>
                        </xsl:when>
                        <xsl:otherwise>
                            <span>Non renseignée</span>
                        </xsl:otherwise>
                    </xsl:choose>
                </div>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Effectif et instrumentation'"/>
                <xsl:with-param name="content" select="$effectContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 3. Section Sources -->
    <xsl:template name="sources-section">
        <xsl:if test="srce_A or srce_alt or srce_chore or cote_srce or srce_code or srce_type or srce_notes or srce_dep or srce_texte or comparaison">
            <xsl:variable name="sourcesContent">
                <xsl:if test="srce_A">
                    <div class="field">
                        <strong>Source A : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_A"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="srce_alt">
                    <div class="field">
                        <strong>Autres sources : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_alt"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="srce_chore">
                    <div class="field">
                        <strong>Source chorégraphique : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_chore"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>

                <xsl:if test="cote_srce">
                    <div class="field">
                        <strong>Cote source : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="cote_srce"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="srce_code">
                    <div class="field">
                        <strong>Code source : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_code"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="srce_type">
                    <div class="field">
                        <strong>Type de source : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_type"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="srce_notes">
                    <div class="field work-text">
                        <strong>Notes sur la source : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_notes"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="srce_dep">
                    <div class="field work-text">
                        <strong>Dépouillement : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_dep"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>

                <xsl:if test="srce_texte">
                    <div class="field">
                        <strong>Description de la source : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="srce_texte"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>

                <xsl:if test="comparaison">
                    <div class="field">
                        <strong>Comparaison sources : </strong>
                        <span><xsl:value-of select="comparaison"/></span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Source(s)'"/>
                <xsl:with-param name="content" select="$sourcesContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 4. Section Informations textuelles -->
    <xsl:template name="informations-textuelles-section">
        <xsl:if test="texte_not or traduc or argument or comm">
            <xsl:variable name="texteInfoContent">
                <xsl:if test="texte_not">
                    <div class="field work-text">
                        <strong>Note sur le texte : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="texte_not"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="traduc">
                    <div class="field">
                        <strong>Traduction : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="traduc"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>

                <xsl:if test="argument">
                    <div class="field work-text">
                        <strong>Argument : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="argument"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>

                <xsl:if test="comm">
                    <div class="field work-text">
                        <strong>Commentaires contemporains : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="comm"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Informations sur le texte'"/>
                <xsl:with-param name="content" select="$texteInfoContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 5. Section Références & mentions -->
    <xsl:template name="references-section">
        <xsl:if test="ref_bibl or notice_bibl or voir_aussi or ed_moderne or disco or catal or oeuv_par">
            <xsl:variable name="referencesContent">
                <xsl:if test="ref_bibl">
                    <div class="field">
                        <strong>Référence bibliographique : </strong>
                        <span><xsl:value-of select="ref_bibl"/></span>
                    </div>
                </xsl:if>

                <xsl:if test="notice_bibl">
                    <div class="field">
                        <strong>Notice bibliographique : </strong>
                        <xsl:call-template name="format-notice-ligne">
                            <xsl:with-param name="texte" select="notice_bibl"/>
                        </xsl:call-template>
                    </div>
                </xsl:if>

                <xsl:if test="voir_aussi">
                    <div class="field">
                        <strong>Voir aussi : </strong>
                        <span><xsl:value-of select="voir_aussi"/></span>
                    </div>
                </xsl:if>

                <xsl:if test="ed_moderne">
                    <div class="field">
                        <strong>Édition moderne : </strong>
                        <span><xsl:value-of select="ed_moderne"/></span>
                    </div>
                </xsl:if>

                <xsl:if test="disco">
                    <div class="field">
                        <strong>Discographie : </strong>
                        <span><xsl:value-of select="disco"/></span>
                    </div>
                </xsl:if>

                <xsl:if test="catal">
                    <div class="field">
                        <strong>Catalogue cité : </strong>
                        <span><xsl:value-of select="catal"/></span>
                    </div>
                </xsl:if>

                <xsl:if test="oeuv_par">
                    <div class="field">
                        <strong>Œuvre parodié : </strong>
                        <span><xsl:value-of select="oeuv_par"/></span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Références et catalogues'"/>
                <xsl:with-param name="content" select="$referencesContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 6. Section Production scénique -->
    <xsl:template name="production-scenique-section">
        <xsl:if test="costume or decor or evnt">
            <xsl:variable name="productionContent">
                <xsl:if test="costume">
                    <div class="field">
                        <strong>Costumes : </strong>
                        <span><xsl:value-of select="costume"/></span>
                    </div>
                </xsl:if>
                
                <xsl:if test="decor">
                    <div class="field">
                        <strong>Décor : </strong>
                        <span><xsl:value-of select="decor"/></span>
                    </div>
                </xsl:if>
                
                <xsl:if test="evnt">
                    <div class="field">
                        <strong>Événement : </strong>
                        <span><xsl:value-of select="evnt"/></span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Production scénique'"/>
                <xsl:with-param name="content" select="$productionContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 7. Section Dates & lieux -->
    <xsl:template name="dates-lieux-section">
        <xsl:if test="date_citee or date_notes or lieu_cite or lieu_notes">
            <xsl:variable name="datesLieuxContent">
                
                <xsl:if test="date_notes">
                    <div class="field">
                        <strong>Note sur les dates : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="date_notes"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="lieu_cite">
                    <div class="field">
                        <strong>Lieu cité : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="lieu_cite"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="lieu_notes">
                    <div class="field">
                        <strong>Notes sur le lieu : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="lieu_notes"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Dates et lieux'"/>
                <xsl:with-param name="content" select="$datesLieuxContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 8. Section Liturgie -->
    <xsl:template name="liturgie-section">
        <xsl:if test="liturg or liturg_notes">
            <xsl:variable name="liturgieContent">
                <xsl:if test="liturg">
                    <div class="field">
                        <strong>Occasion liturgique : </strong><br/>
                        <span>
                            <xsl:call-template name="format-with-br">
                                <xsl:with-param name="text" select="liturg"/>
                            </xsl:call-template>
                        </span>
                    </div>
                </xsl:if>
                
                <xsl:if test="liturg_notes">
                    <div class="field">
                        <strong>Notes sur la liturgie : </strong>
                        <span><xsl:value-of select="liturg_notes"/></span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Liturgie'"/>
                <xsl:with-param name="content" select="$liturgieContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 9. Section Personnages, rôles, noms -->
    <xsl:template name="roles-personnages-section">
        <xsl:if test="role_cite or role_notes or nom_cite or nom_notes">
            <xsl:variable name="rolesContent">
                <xsl:if test="role_cite">
                    <div class="field">
                        <strong>Rôle(s) cité(s) : </strong>
                        <span><xsl:value-of select="role_cite"/></span>
                    </div>
                </xsl:if>
                
                <xsl:if test="role_notes">
                    <div class="field">
                        <strong>Notes sur le ou les rôles : </strong>
                        <span><xsl:value-of select="role_notes"/></span>
                    </div>
                </xsl:if>
                
                <xsl:if test="nom_cite">
                    <div class="field">
                        <strong>Noms cités : </strong>
                        <span><xsl:value-of select="nom_cite"/></span>
                    </div>
                </xsl:if>
                
                <xsl:if test="nom_notes">
                    <div class="field">
                        <strong>Note sur les noms cités : </strong>
                        <span><xsl:value-of select="nom_notes"/></span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Rôles et personnages'"/>
                <xsl:with-param name="content" select="$rolesContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 10. Section Notes et attributions -->
    <xsl:template name="notes-attributions-section">
        <xsl:if test="notes or notes_attrib">
            <xsl:variable name="notesContent">
                <xsl:if test="notes">
                    <div class="field">
                        <strong>Notes et références : </strong>
                        <span><xsl:value-of select="notes"/></span>
                    </div>
                </xsl:if>
                
                <xsl:if test="notes_attrib">
                    <div class="field">
                        <strong>Notes sur l'attribution : </strong>
                        <span><xsl:value-of select="notes_attrib"/></span>
                    </div>
                </xsl:if>
            </xsl:variable>

            <xsl:call-template name="accordeon">
                <xsl:with-param name="title" select="'Notes et attributions'"/>
                <xsl:with-param name="content" select="$notesContent/node()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- 11. Section Responsable de la saisie -->
    <xsl:template name="auteur-saisie-section">
        <xsl:if test="aut_saisie">
            <div class="field">
                <strong>Auteur de la saisie : </strong>
                <span><xsl:value-of select="aut_saisie"/></span>
            </div>
        </xsl:if>
    </xsl:template>

    <xsl:template name="liste-fragments-oeuvre">
        <xsl:if test="a_pour_fragments">
            <div class="fragments-liste">
                <h3>Fragments de cette œuvre :</h3>
                <ul>
                    <xsl:variable name="doc-root" select="/"/>
                    <xsl:variable name="projet-courant" select="projet"/>
                    <xsl:variable name="fragments-ids" select="tokenize(a_pour_fragments, ' - ')"/>

                    <xsl:for-each select="$fragments-ids[position() &gt; 1]">
                        <xsl:variable name="fragment-number" select="normalize-space(.)"/>
                        <xsl:variable name="fragment-number-padded" select="format-number(number($fragment-number), '00000')"/>

                        <xsl:for-each select="$doc-root//item[projet = $projet-courant and nature = 'Fragment']">
                            <xsl:variable name="num-orig-fragment" select="num_orig"/>
                            <xsl:variable name="last-five-digits" select="substring($num-orig-fragment, string-length($num-orig-fragment) - 4)"/>

                            <xsl:if test="$last-five-digits = $fragment-number-padded">
                                <li>
                                    <a href="../fragments/{numero}.html">
                                        <xsl:value-of select="frag"/>
                                    </a>
                                </li>
                            </xsl:if>
                        </xsl:for-each>
                    </xsl:for-each>
                </ul>
            </div>
        </xsl:if>
    </xsl:template>

    <xsl:template name="oeuvre-parente-fragment">
        <xsl:if test="fragment_de">
            <div class="oeuvre-parente">
                <h3>Œuvre parente :</h3>
                
                <xsl:variable name="doc-root" select="/"/>
                <xsl:variable name="projet-courant" select="projet"/>
                <xsl:variable name="oeuvre-id" select="normalize-space(fragment_de)"/>
                <xsl:variable name="oeuvre-number" select="substring-after($oeuvre-id, concat($projet-courant, ' - '))"/>
                <xsl:variable name="oeuvre-number-padded" select="format-number(number($oeuvre-number), '00000')"/>

                <xsl:for-each select="$doc-root//item[projet = $projet-courant and nature = 'Oeuvre']">
                    <xsl:variable name="num-orig-oeuvre" select="num_orig"/>
                    <xsl:variable name="last-five-digits" select="substring($num-orig-oeuvre, string-length($num-orig-oeuvre) - 4)"/>

                    <xsl:if test="$last-five-digits = $oeuvre-number-padded">
                        <p>
                            <a href="../works/{numero}.html">
                                <xsl:value-of select="oeuvre"/>
                            </a>
                        </p>
                    </xsl:if>
                </xsl:for-each>
            </div>
        </xsl:if>
    </xsl:template>

    <xsl:template name="accordeon">
        <xsl:param name="title"/>
        <xsl:param name="content"/>

        <div class="accordeon">
            <div class="header">
            <h3><xsl:value-of select="$title"/></h3>
            <span class="separator"></span>
            <span class="chevron">›</span>
            </div>
            <div class="content">
            <xsl:copy-of select="$content"/>
            </div>
        </div>
    </xsl:template>

    <xsl:template name="format-notice-ligne">
        <xsl:param name="texte"/>

        <!-- 1. Tronquer à la première double ligne vide (deux retours à la ligne consécutifs) -->
        <xsl:variable name="tronque" select="replace($texte, '([\r\n]+){2,}.*$', '')"/>

        <!-- 2. Remplacer les slashs typographiques " / " par · -->
        <xsl:variable name="remplace-slash" select="replace($tronque, ' / ', ' · ')"/>

        <!-- 3. Remplacer les retours à la ligne restants par · -->
        <xsl:variable name="remplace-retours" select="replace($remplace-slash, '[&#xD;&#xA;]+', ' · ')"/>

        <!-- 4. Nettoyer les · successifs et espaces inutiles -->
        <xsl:variable name="nettoye" select="replace(normalize-space($remplace-retours), '· +', '· ')"/>

        <xsl:value-of select="$nettoye"/>
    </xsl:template>


    <xsl:template name="format-with-br">
        <xsl:param name="text"/>
        <xsl:choose>
            <!-- Gestion CRLF -->
            <xsl:when test="contains($text, '&#xD;&#xA;')">
                <xsl:value-of select="substring-before($text, '&#xD;&#xA;')"/>
                <br/>
                <xsl:call-template name="format-with-br">
                    <xsl:with-param name="text" select="substring-after($text, '&#xD;&#xA;')"/>
                </xsl:call-template>
            </xsl:when>
            <!-- Gestion CR -->
            <xsl:when test="contains($text, '&#xD;')">
                <xsl:value-of select="substring-before($text, '&#xD;')"/>
                <br/>
                <xsl:call-template name="format-with-br">
                    <xsl:with-param name="text" select="substring-after($text, '&#xD;')"/>
                </xsl:call-template>
            </xsl:when>
            <!-- Gestion LF -->
            <xsl:when test="contains($text, '&#xA;')">
                <xsl:value-of select="substring-before($text, '&#xA;')"/>
                <br/>
                <xsl:call-template name="format-with-br">
                    <xsl:with-param name="text" select="substring-after($text, '&#xA;')"/>
                </xsl:call-template>
            </xsl:when>
            <!-- Balises br textuelles -->
            <xsl:when test="contains($text, '&lt;br/&gt;')">
                <xsl:value-of select="substring-before($text, '&lt;br/&gt;')" disable-output-escaping="yes"/>
                <br/>
                <xsl:call-template name="format-with-br">
                    <xsl:with-param name="text" select="substring-after($text, '&lt;br/&gt;')"/>
                </xsl:call-template>
            </xsl:when>
            <!-- Fin -->
            <xsl:otherwise>
                <xsl:value-of select="$text"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- Template pour le logo animé du CMBV -->
    <xsl:template name="cmbv-logo">
        <a href="https://cmbv.fr/fr/ressources/ressources-numeriques" title="CMBV - Ressources numériques">
            <div class="logo">                
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 280" id="svg-logo-animation" class="svg-logo-animation logo-loaded">
                        <mask id="myClip">
                            <rect x="0" y="0" width="300" height="280" fill="#fff"></rect>
                            <!-- <circle cx="150" cy="140" r="53" fill="#000"/> -->
                            <circle cx="150" cy="140" r="53" fill="#000"></circle>
                        </mask>
                        <g class="logo-lines-container">
                            <g mask="url(#myClip)" class="logo-lines"><rect width="2" height="38" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.99452,-0.10453,0.12636,1.20228,-11.329545069680176,40.06825867695078)" data-svg-origin="150 140"></rect><rect width="2" height="45" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.97815,-0.20791,0.22904,1.07758,-17.769338555860152,72.16751169056522)" data-svg-origin="150 140"></rect><rect width="2" height="36" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.95106,-0.30902,0.29883,0.91971,-18.117265209398873,107.99893388760962)" data-svg-origin="150 140"></rect><rect width="2" height="33" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.91355,-0.40674,0.34785,0.7813,-14.174562384308896,140.04677867634018)" data-svg-origin="150 140"></rect><rect width="2" height="22" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.86603,-0.5,0.60924,1.05524,-38.69796611181344,113.16558664437247)" data-svg-origin="150 140"></rect><rect width="2" height="73" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.80901,-0.58778,0.62534,0.86071,-27.748124134354292,150.54570693755363)" data-svg-origin="150 140"></rect><rect width="2" height="50" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.74314,-0.66913,0.87766,0.97475,-48.880865944512564,143.2916724229006)" data-svg-origin="150 140"></rect><rect width="2" height="34" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.66912,-0.74315,0.95997,0.86436,-45.37909544698567,165.92464405511473)" data-svg-origin="150 140"></rect><rect width="2" height="38" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.58779,-0.80901,0.80619,0.58573,-8.15657360420309,210.50249877924583)" data-svg-origin="150 140"></rect><rect width="2" height="23" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.5,-0.86603,0.69294,0.40007,23.88722453337798,240.39395100249305)" data-svg-origin="150 140"></rect><rect width="2" height="35" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.40673,-0.91355,0.79527,0.35407,26.07024496877783,249.01865279579738)" data-svg-origin="150 140"></rect><rect width="2" height="49" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.30901,-0.95106,1.13244,0.36795,-4.487753889875179,247.523181632022)" data-svg-origin="150 140"></rect><rect width="2" height="30" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.20791,-0.97815,1.03792,0.22061,25.345488326059453,266.8551517393764)" data-svg-origin="150 140"></rect><rect width="2" height="38" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.10453,-0.99452,1.22795,0.12906,15.116878670901961,276.6490922640765)" data-svg-origin="150 140"></rect><rect width="2" height="23" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0,-1,1.34645,0,14.49609426813791,290)" data-svg-origin="150 140"></rect><rect width="2" height="32" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.10453,-0.99452,1.12882,-0.11864,60.35368463076976,300.2482252871191)" data-svg-origin="150 140"></rect><rect width="2" height="25" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.20791,-0.97815,1.15879,-0.2463,70.79716158435089,310.1856554965983)" data-svg-origin="150 140"></rect><rect width="2" height="36" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.30902,-0.95106,1.02192,-0.33204,103.68934540104614,312.76676054525353)" data-svg-origin="150 140"></rect><rect width="2" height="93" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.40674,-0.91355,0.83009,-0.36958,143.21592448557413,307.2159645938784)" data-svg-origin="150 140"></rect><rect width="2" height="23" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.5,-0.86603,0.72696,-0.41971,169.1253417040736,302.16342998275263)" data-svg-origin="150 140"></rect><rect width="2" height="35" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.58778,-0.80902,0.64807,-0.47085,190.31553505269937,296.1190836090255)" data-svg-origin="150 140"></rect><rect width="2" height="70" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.66913,-0.74314,0.69324,-0.62419,192.70276325770504,303.39513961026955)" data-svg-origin="150 140"></rect><rect width="2" height="84" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.74314,-0.66913,0.68129,-0.75665,201.55440033511147,306.91394337566976)" data-svg-origin="150 140"></rect><rect width="2" height="27" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.80901,-0.58779,0.52614,-0.72416,228.84589677474764,286.67264154084563)" data-svg-origin="150 140"></rect><rect width="2" height="45" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.86603,-0.5,0.46341,-0.80266,241.52539637212664,281.4734341996944)" data-svg-origin="150 140"></rect><rect width="2" height="38" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.91355,-0.40673,0.48184,-1.08223,241.1317256712291,304.10436930975226)" data-svg-origin="150 140"></rect><rect width="2" height="31" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.95106,-0.30901,0.26863,-0.82677,271.4277215920854,251.69373963701804)" data-svg-origin="150 140"></rect><rect width="2" height="15" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.97815,-0.20791,0.27562,-1.2967,269.1545827527095,300.8836238778186)" data-svg-origin="150 140"></rect><rect width="2" height="28" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.99452,-0.10453,0.08817,-0.83896,292.3730091595228,220.4248942951438)" data-svg-origin="150 140"></rect><rect width="2" height="75" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-1,0,0,-1.12772,300,244.8816133880241)" data-svg-origin="150 140"></rect><rect width="2" height="63" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.99452,0.10453,-0.11164,-1.06221,309.2681745950866,220.3218107558164)" data-svg-origin="150 140"></rect><rect width="2" height="18" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.97815,0.20791,-0.19059,-0.89666,312.3852507682159,182.5043310034644)" data-svg-origin="150 140"></rect><rect width="2" height="86" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.95106,0.30901,-0.25298,-0.77861,311.69866496583563,152.2467655893068)" data-svg-origin="150 140"></rect><rect width="2" height="30" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.91355,0.40673,-0.33629,-0.75531,312.55514828913755,136.31574504484826)" data-svg-origin="150 140"></rect><rect width="2" height="38" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.86603,0.5,-0.42004,-0.72753,312.20966923796465,120.954747460309)" data-svg-origin="150 140"></rect><rect width="2" height="20" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.80901,0.58779,-0.47022,-0.64721,306.03153620902435,99.5639668143808)" data-svg-origin="150 140"></rect><rect width="2" height="31" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.74314,0.66913,-0.55191,-0.61296,303.2755585864879,86.05821497100487)" data-svg-origin="150 140"></rect><rect width="2" height="23" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.66913,0.74314,-0.82644,-0.74412,326.6844699026451,97.24255203654296)" data-svg-origin="150 140"></rect><rect width="2" height="33" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.58778,0.80902,-0.94642,-0.68762,327.7888552537097,83.76125441346075)" data-svg-origin="150 140"></rect><rect width="2" height="56" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.5,0.86603,-0.9191,-0.53064,307.77492482558574,57.88642367907908)" data-svg-origin="150 140"></rect><rect width="2" height="72" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.40674,0.91355,-0.84112,-0.37449,280.34975424238104,33.84000212965473)" data-svg-origin="150 140"></rect><rect width="2" height="33" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.30902,0.95106,-0.9596,-0.31179,280.2896970449943,24.614507876310768)" data-svg-origin="150 140"></rect><rect width="2" height="27" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.20791,0.97815,-1.25031,-0.26575,304.38883878704195,19.46512267261044)" data-svg-origin="150 140"></rect><rect width="2" height="32" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(-0.10453,0.99452,-0.9941,-0.10448,252.14471163630074,-0.09042645563433016)" data-svg-origin="150 140"></rect><rect width="2" height="22" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0,1,-0.89594,0,222.43204714688113,-10)" data-svg-origin="150 140"></rect><rect width="2" height="58" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.10453,0.99452,-1.0112,0.10628,223.18055694290138,-18.517886109119473)" data-svg-origin="150 140"></rect><rect width="2" height="74" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.20791,0.97815,-0.93761,0.19929,198.23667022921722,-23.604184186839017)" data-svg-origin="150 140"></rect><rect width="2" height="52" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.30901,0.95106,-0.94624,0.30745,185.71482687718074,-29.323946545524414)" data-svg-origin="150 140"></rect><rect width="2" height="30" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.40673,0.91355,-0.89103,0.39671,165.31555680277054,-31.01433725462084)" data-svg-origin="150 140"></rect><rect width="2" height="42" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.5,0.86603,-0.87177,0.50331,151.14851171887722,-33.86828259233358)" data-svg-origin="150 140"></rect><rect width="2" height="28" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.58779,0.80901,-0.73558,0.53443,121.93548884844003,-25.019912311468907)" data-svg-origin="150 140"></rect><rect width="2" height="18" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.66912,0.74315,-0.78382,0.70575,119.9789065136654,-34.81377650607398)" data-svg-origin="150 140"></rect><rect width="2" height="27" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.74314,0.66913,-0.66359,0.73699,95.96713848483076,-24.161955959233552)" data-svg-origin="150 140"></rect><rect width="2" height="28" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.80901,0.58778,-0.59013,0.81225,80.11356612191544,-19.004805772388124)" data-svg-origin="150 140"></rect><rect width="2" height="35" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.86603,0.5,-0.53825,0.93229,68.95227241780887,-19.621238791990095)" data-svg-origin="150 140"></rect><rect width="2" height="45" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.91355,0.40674,-0.42448,0.9534,50.83838098871224,-6.068268943890629)" data-svg-origin="150 140"></rect><rect width="2" height="35" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.95106,0.30902,-0.35364,1.0884,40.47373713684854,-8.322941140933281)" data-svg-origin="150 140"></rect><rect width="2" height="30" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.97815,0.20791,-0.17357,0.81661,16.559301505179086,46.32931877595625)" data-svg-origin="150 140"></rect><rect width="2" height="46" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(0.99452,0.10453,-0.11228,1.0683,11.001384253069046,27.467875879056457)" data-svg-origin="150 140"></rect><rect width="2" height="30" x="150" y="140" rx="2" ry="2" class="logo-line" transform="matrix(1,0,0,0.84107,0,75.24947735668239)" data-svg-origin="150 140"></rect></g>
                        </g>
                        
                        <g class="logo-text">
                            <path class="st0" d="M135.6,137.7c4.4,0.2,8.5-2.1,10.7-5.9c0.1-0.2,0.2-0.4,0.2-0.7c0-0.7-0.6-1.3-1.3-1.3c0,0,0,0,0,0
                            c-0.4,0-0.9,0.2-1.1,0.6c-1.7,3.1-5,5-8.5,4.9c-6.2,0-10.3-4.4-10.3-11c0-6.4,4.3-10.9,10.5-10.9c3.4-0.2,6.7,1.7,8.3,4.7
                            c0.2,0.4,0.7,0.7,1.1,0.7c0.7,0,1.3-0.5,1.3-1.2c0,0,0,0,0-0.1c0-0.3-0.1-0.5-0.2-0.7c-2.1-3.7-6.2-6-10.5-5.8
                            c-7.1-0.1-13,5.6-13.1,12.7c0,0.2,0,0.4,0,0.6c-0.1,3.6,1.3,7.1,3.8,9.7C128.9,136.4,132.2,137.7,135.6,137.7"></path>
                            <path class="st0" d="M155.6,137.3c0.7,0,1.3-0.5,1.3-1.2c0,0,0,0,0,0v-20c0-0.3,0-0.7-0.1-1c0.1,0.3,0.2,0.6,0.4,0.8l7.4,14.2
                            c0.2,0.4,0.7,0.7,1.2,0.7c0.5,0,0.9-0.3,1.2-0.7l7.3-14.2c0.2-0.3,0.3-0.7,0.4-1c0,0.4,0,0.8,0,1.2v20c0,0.7,0.6,1.3,1.3,1.3
                            c0,0,0,0,0,0c0.7,0,1.3-0.6,1.3-1.3c0,0,0,0,0,0v-23.4c0-0.7-0.6-1.3-1.3-1.3h-1.4c-0.5,0-0.9,0.3-1.1,0.7l-7.8,15.2L158,112
                            c-0.2-0.4-0.6-0.7-1.1-0.7h-1.3c-0.7,0-1.2,0.5-1.3,1.2c0,0,0,0,0,0.1v23.5C154.3,136.8,154.9,137.3,155.6,137.3
                            C155.6,137.3,155.6,137.3,155.6,137.3"></path>
                            <path class="st0" d="M129,154.6v-8.5h9.9c3.1,0,5.1,1.7,5.1,4.3s-1.8,4.2-5.1,4.2H129z M145.2,162.1c0,2.5-1.9,5.1-6.1,5.1H129V157
                            h10.1C142.9,157,145.2,159,145.2,162.1 M143.7,155.7c1.9-1.1,3-3.1,2.9-5.3c0-3.9-3.2-6.7-7.8-6.7h-11.2c-0.7,0-1.3,0.6-1.3,1.3
                            c0,0,0,0,0,0v23.4c0,0.7,0.6,1.3,1.3,1.3c0,0,0,0,0,0h11.4c5.2,0,8.7-3,8.7-7.6C147.9,159.3,146.3,156.7,143.7,155.7"></path>
                            <path class="st0" d="M176,143.7c-0.5,0-1,0.3-1.2,0.9l-8.8,21.4c-0.1,0.3-0.2,0.7-0.3,1c-0.1-0.3-0.2-0.7-0.3-1l-8.8-21.3
                            c-0.2-0.6-0.7-1-1.3-1c-0.7,0-1.3,0.6-1.3,1.3c0,0.2,0,0.4,0.1,0.6l9.7,23.3c0.2,0.5,0.6,0.8,1.1,0.8h1.3c0.5,0,1-0.3,1.2-0.8
                            l9.7-23.3c0.1-0.2,0.2-0.4,0.2-0.6C177.3,144.2,176.7,143.6,176,143.7C176,143.6,176,143.6,176,143.7"></path>
                        </g>
                        
                </svg>
            </div>
        </a>
    </xsl:template>

</xsl:stylesheet>
