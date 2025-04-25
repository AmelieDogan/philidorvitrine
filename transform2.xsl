<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>
    
    <!-- Variable pour stocker tous les projets uniques -->
    <xsl:key name="projects" match="//item" use="projet"/>
    
    <!-- Variable pour stocker tous les genres musicaux uniques par projet -->
    <xsl:key name="genres-by-project" match="//item" use="concat(projet, '|', genre_musical)"/>
    
    <!-- Template principal qui gère la création de toutes les pages -->
    <xsl:template match="/">
        <!-- Créer la page d'index principal -->
        <xsl:call-template name="create-index"/>
        
        <!-- Créer une page pour chaque projet -->
        <xsl:for-each select="//item[generate-id(.) = generate-id(key('projects', projet)[1])]">
            <xsl:sort select="projet"/>
            <xsl:call-template name="create-project-page">
                <xsl:with-param name="project" select="projet"/>
            </xsl:call-template>
        </xsl:for-each>
        
        <!-- Créer une page pour chaque œuvre -->
        <xsl:for-each select="//item">
            <xsl:call-template name="create-work-page"/>
        </xsl:for-each>
    </xsl:template>
    
    <!-- Template pour créer la page d'index des projets -->
    <xsl:template name="create-index">
        <xsl:result-document href="output/index.html" method="html">
            <html>
                <head>
                    <title>Centre de Musique Baroque de Versailles - Index des Projets</title>
                    <link rel="stylesheet" type="text/css" href="statics/css/styles.css"/>
                    <meta charset="UTF-8"/>
                </head>
                <body>
                    <header>
                        <div class="rayon"></div>
                        <div class="header-content">
                            <h1>Ressources du pôle recherche</h1>
                            <h2>Base de données PHILIDOR4</h2>
                        </div>
                        <div class="logo"><img src="statics/img/CMBV_Logo-05_noir-rvb.png"/></div>
                    </header>
                    
                    <main>
                        <section class="presentation">
                            <h2>Présentation</h2>
                            <p>PHILIDOR est un portail de ressources numériques qui a pour but de rassembler et diffuser en accès libre des informations sur la musique et les arts du spectacle en France aux XVIIe et XVIIIe siècles. Il s'adresse aux chercheurs et étudiants de différentes disciplines (musicologie, histoire, lettres, arts de la scène, etc.), aux musiciens et plus généralement au public intéressé par ce domaine. PHILIDOR ne couvre pas la totalité du savoir historique sur la musique baroque française, il est le fruit des nombreux travaux menés au Centre depuis vingt ans et est constitué d'environ 20 000 notices.</p>
                        </section>
                        <section class="index-content">
                            <h2>Catalogues d'auteur</h2>
                            <p>Sélectionnez un auteur pour voir les œuvres associées :</p>
                            
                            <ul class="project-list">
                                <xsl:for-each select="//item[generate-id(.) = generate-id(key('projects', projet)[1])]">
                                    <xsl:sort select="projet"/>
                                    <li>
                                        <a href="projects/{translate(projet, ' ', '_')}.html">
                                            <xsl:value-of select="projet"/>
                                        </a>
                                        <span class="work-count">
                                            (<xsl:value-of select="count(//item[projet = current()/projet])"/> œuvres)
                                        </span>
                                    </li>
                                </xsl:for-each>
                            </ul>
                        </section>
                    </main>
                    
                    <footer>
                        <p>© Centre de Musique Baroque de Versailles - Base de données PHILIDOR4</p>
                        <p class="smaller">Faire rayonner la musique française des XVIIe et XVIIIe siècles</p>
                    </footer>
                </body>
            </html>
        </xsl:result-document>
    </xsl:template>
    
    <!-- Template pour créer une page de projet avec la liste des œuvres organisées par genre -->
    <xsl:template name="create-project-page">
        <xsl:param name="project"/>
        
        <xsl:result-document href="output/projects/{translate($project, ' ', '_')}.html" method="html">
            <html>
                <head>
                    <title>Projet : <xsl:value-of select="$project"/> - CMBV</title>
                    <link rel="stylesheet" type="text/css" href="../statics/css/styles.css"/>
                    <meta charset="UTF-8"/>
                </head>
                <body>
                    <header>
                        <div class="rayon"></div>
                        <div class="header-content">
                            <h1>Ressources du pôle recherche</h1>
                            <nav>
                                <a href="../index.html">Retour à l'index des projets</a>
                            </nav>
                        </div>
                        <div class="logo"><img src="../statics/img/CMBV_Logo-05_noir-rvb.png"/></div>
                    </header>
                    
                    <main>
                        <section class="project-content">
                            <h2>Projet : <xsl:value-of select="$project"/></h2>
                            
                            <!-- Sommaire des genres pour ce projet -->
                            <xsl:variable name="project-items" select="//item[projet = $project]"/>
                            <xsl:variable name="genres" select="$project-items[generate-id(.) = 
                                                          generate-id(key('genres-by-project', 
                                                                    concat($project, '|', genre_musical))[1])]"/>
                            
                            <div class="genre-summary">
                                <h3>Sommaire des genres</h3>
                                <ul class="genre-links">
                                    <xsl:for-each select="$genres">
                                        <xsl:sort select="genre_musical"/>
                                        <xsl:variable name="genre" select="genre_musical"/>
                                        <xsl:if test="string-length(normalize-space($genre)) > 0">
                                            <li>
                                                <a href="#{translate($genre, ' ,;.:', '_____')}">
                                                    <xsl:value-of select="$genre"/>
                                                </a>
                                                <span class="work-count">
                                                    (<xsl:value-of select="count($project-items[genre_musical = $genre])"/> œuvres)
                                                </span>
                                            </li>
                                        </xsl:if>
                                    </xsl:for-each>
                                    
                                    <!-- Lien pour la section "Divers" si des œuvres sans genre existent -->
                                    <xsl:if test="count($project-items[string-length(normalize-space(genre_musical)) = 0]) > 0">
                                        <li>
                                            <a href="#divers">Divers</a>
                                            <span class="work-count">
                                                (<xsl:value-of select="count($project-items[string-length(normalize-space(genre_musical)) = 0])"/> œuvres)
                                            </span>
                                        </li>
                                    </xsl:if>
                                </ul>
                            </div>
                            
                            <!-- Afficher les œuvres par genre -->
                            <xsl:for-each select="$genres">
                                <xsl:sort select="genre_musical"/>
                                <xsl:variable name="genre" select="genre_musical"/>
                                <xsl:if test="string-length(normalize-space($genre)) > 0">
                                    <section class="genre-section" id="{translate($genre, ' ,;.:', '_____')}">
                                        <h3><xsl:value-of select="$genre"/></h3>
                                        <ul class="work-list single-column">
                                            <xsl:for-each select="$project-items[genre_musical = $genre]">
                                                <xsl:sort select="oeuvre"/>
                                                <li>
                                                    <a href="../works/{numero}.html">
                                                        <xsl:choose>
                                                            <xsl:when test="oeuvre != ''">
                                                                <xsl:value-of select="oeuvre"/>
                                                            </xsl:when>
                                                            <xsl:otherwise>
                                                                <em>Titre non spécifié</em>
                                                            </xsl:otherwise>
                                                        </xsl:choose>
                                                    </a>
                                                </li>
                                            </xsl:for-each>
                                        </ul>
                                    </section>
                                </xsl:if>
                            </xsl:for-each>
                            
                            <!-- Section pour les œuvres sans genre (Divers) -->
                            <xsl:if test="count($project-items[string-length(normalize-space(genre_musical)) = 0]) > 0">
                                <section class="genre-section" id="divers">
                                    <h3>Divers</h3>
                                    <ul class="work-list single-column">
                                        <xsl:for-each select="$project-items[string-length(normalize-space(genre_musical)) = 0]">
                                            <xsl:sort select="oeuvre"/>
                                            <li>
                                                <a href="../works/{numero}.html">
                                                    <xsl:choose>
                                                        <xsl:when test="oeuvre != ''">
                                                            <xsl:value-of select="oeuvre"/>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <em>Titre non spécifié</em>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </a>
                                            </li>
                                        </xsl:for-each>
                                    </ul>
                                </section>
                            </xsl:if>
                            
                            <div class="back-to-top">
                                <a href="#">▲</a>
                            </div>
                        </section>
                    </main>
                    
                    <footer>
                        <p>© Centre de Musique Baroque de Versailles - Base de données PHILIDOR4</p>
                        <p class="smaller">Faire rayonner la musique française des XVIIe et XVIIIe siècles</p>
                    </footer>
                </body>
            </html>
        </xsl:result-document>
    </xsl:template>
    
    <!-- Template pour créer une page détaillée pour chaque œuvre -->
    <xsl:template name="create-work-page">
        <!-- Vérifiez que numero n'est pas vide -->
        <xsl:if test="string-length(normalize-space(numero)) > 0">
            <xsl:result-document href="output/works/{numero}.html" method="html">
                <html>
                    <head>
                        <title>
                            <xsl:choose>
                                <xsl:when test="oeuvre != ''">
                                    <xsl:value-of select="oeuvre"/> - CMBV
                                </xsl:when>
                                <xsl:otherwise>
                                    Œuvre #<xsl:value-of select="numero"/> - CMBV
                                </xsl:otherwise>
                            </xsl:choose>
                        </title>
                        <link rel="stylesheet" type="text/css" href="../statics/css/styles.css"/>
                        <meta charset="UTF-8"/>
                    </head>
                    <body>
                        <header>
                            <div class="rayon"></div>
                            <div class="header-content">
                                <h1>Ressources du pôle recherche</h1>
                                <nav>
                                    <a href="../index.html">Index des projets</a> &gt;
                                    <a href="../projects/{translate(projet, ' ', '_')}.html">
                                        Projet <xsl:value-of select="projet"/>
                                    </a>
                                </nav>
                            </div>
                            <div class="logo"><img src="../statics/img/CMBV_Logo-05_noir-rvb.png"/></div>
                        </header>
                        
                        <main>
                            <article class="work-details">
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
                                
                                <dl class="metadata">
                                    <!-- Informations principales -->
                                    <dt>Identifiant</dt>
                                    <dd><xsl:value-of select="numero"/> (origine: <xsl:value-of select="num_orig"/>)</dd>
                                    
                                    <xsl:if test="genre_musical != ''">
                                        <dt>Genre musical</dt>
                                        <dd><xsl:value-of select="genre_musical"/></dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="genre_texte != ''">
                                        <dt>Genre textuel</dt>
                                        <dd><xsl:value-of select="genre_texte"/></dd>
                                    </xsl:if>
                                    
                                    <!-- Personnes associées -->
                                    <xsl:if test="nom != ''">
                                        <dt>Personnes</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="nom"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="fonct != ''">
                                        <dt>Fonctions</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="fonct"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <!-- Dates et lieux -->
                                    <xsl:if test="date_notes != '' or date_citee != ''">
                                        <dt>Dates</dt>
                                        <dd>
                                            <xsl:if test="date_citee != ''">
                                                <strong>Dates citées :</strong>
                                                <xsl:call-template name="format-with-br">
                                                    <xsl:with-param name="text" select="date_citee"/>
                                                </xsl:call-template>
                                            </xsl:if>
                                            <xsl:if test="date_notes != ''">
                                                <xsl:if test="date_citee != ''"><br/></xsl:if>
                                                <strong>Notes sur les dates :</strong>
                                                <xsl:value-of select="date_notes"/>
                                            </xsl:if>
                                        </dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="lieu_cite != '' or lieu_notes != ''">
                                        <dt>Lieux</dt>
                                        <dd>
                                            <xsl:if test="lieu_cite != ''">
                                                <strong>Lieux cités :</strong>
                                                <xsl:call-template name="format-with-br">
                                                    <xsl:with-param name="text" select="lieu_cite"/>
                                                </xsl:call-template>
                                            </xsl:if>
                                            <xsl:if test="lieu_notes != ''">
                                                <xsl:if test="lieu_cite != ''"><br/></xsl:if>
                                                <strong>Notes sur les lieux :</strong>
                                                <xsl:value-of select="lieu_notes"/>
                                            </xsl:if>
                                        </dd>
                                    </xsl:if>
                                    
                                    <!-- Caractéristiques musicales -->
                                    <xsl:if test="effectif != '' or effectif_not != ''">
                                        <dt>Effectif</dt>
                                        <dd>
                                            <xsl:if test="effectif != ''">
                                                <strong>Description :</strong> <xsl:value-of select="effectif"/>
                                            </xsl:if>
                                            <xsl:if test="effectif_not != ''">
                                                <xsl:if test="effectif != ''"><br/></xsl:if>
                                                <strong>Notes :</strong> <xsl:value-of select="effectif_not"/>
                                            </xsl:if>
                                        </dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="inc_lat != ''">
                                        <dt>Incipit latin</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="inc_lat"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="inc_mus != ''">
                                        <dt>Incipit musical</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="inc_mus"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <!-- Sources -->
                                    <xsl:if test="srce_A != ''">
                                        <dt>Source A</dt>
                                        <dd><xsl:value-of select="srce_A"/></dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="srce_alt != ''">
                                        <dt>Source alternative</dt>
                                        <dd><xsl:value-of select="srce_alt"/></dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="srce_notes != ''">
                                        <dt>Notes sur les sources</dt>
                                        <dd><xsl:value-of select="srce_notes"/></dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="cote_srce != ''">
                                        <dt>Cotes des sources</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="cote_srce"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <!-- Notes et commentaires -->
                                    <xsl:if test="notes != ''">
                                        <dt>Notes</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="notes"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="liturg != ''">
                                        <dt>Liturgie</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="liturg"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <!-- Texte de l'œuvre si disponible -->
                                    <xsl:if test="srce_texte != ''">
                                        <dt>Texte</dt>
                                        <dd class="work-text">
                                            <xsl:value-of select="srce_texte" disable-output-escaping="yes"/>
                                        </dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="texte_not != ''">
                                        <dt>Notes sur le texte</dt>
                                        <dd>
                                            <xsl:call-template name="format-with-br">
                                                <xsl:with-param name="text" select="texte_not"/>
                                            </xsl:call-template>
                                        </dd>
                                    </xsl:if>
                                    
                                    <xsl:if test="ref_bibl != ''">
                                        <dt>Références bibliographiques</dt>
                                        <dd><xsl:value-of select="ref_bibl"/></dd>
                                    </xsl:if>
                                </dl>
                            </article>
                        </main>
                        
                        <footer>
                            <p>© Centre de Musique Baroque de Versailles - Base de données PHILIDOR4</p>
                            <p class="smaller">
                                Page générée à partir des données Philidor4 | 
                                Auteur de la saisie : <xsl:value-of select="aut_saisie"/>
                            </p>
                        </footer>
                    </body>
                </html>
            </xsl:result-document>
        </xsl:if>
    </xsl:template>
    
    <!-- Template utilitaire pour formater du texte avec des balises <br/> -->
    <xsl:template name="format-with-br">
        <xsl:param name="text"/>
        <xsl:choose>
            <xsl:when test="contains($text, '&#10;')">
                <xsl:value-of select="substring-before($text, '&#10;')"/>
                <br/>
                <xsl:call-template name="format-with-br">
                    <xsl:with-param name="text" select="substring-after($text, '&#10;')"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="contains($text, '&lt;br/&gt;')">
                <xsl:value-of select="substring-before($text, '&lt;br/&gt;')" disable-output-escaping="yes"/>
                <br/>
                <xsl:call-template name="format-with-br">
                    <xsl:with-param name="text" select="substring-after($text, '&lt;br/&gt;')"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$text"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>