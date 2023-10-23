#! /usr/bin/env python3
"""
    LINKEDIN_ANALYSE_POST permet d'analyser un post Linkedin.

    Nécessite de :
    1. chercher 'CreatedTime' dans l'inspecteur de la page Linkedin sur laquelle se trouve
    2. copier-coller la partie dictionnaire dans le fichier texte linkedin.txt
"""

import datetime
import json
import os
import re
from urllib.parse import quote

#=== PARAMETRES ===
dossier             = os.path.dirname(__file__) + '/'
linkedin_data_file  = 'linkedin_data.txt'                   # Par défaut
linkedin_json_file  = 'linkedin_json.json'                  # Par défaut
filtre_comment      = [ '$type', '*socialDetail', 'actions', 'annotation', 'annotationActionType', 'canDelete', 'commentPrompt', 'content', 'contributed', 'createdDuringLiveEvent',
                        'dashEntityUrn', 'dashParentCommentUrn', 'dashTranslationUrn', 'displayReason', 'entityUrn', 'groupMembership', 'headline', 'insight', 
                        'index', 'parentCommentBackendUrn', 'pinned', 'rootSocialPermissions', 'threadUrn', 'translatedText', 'translationUrn'] #]
filtre_comment2     = [ '$type', 'additionalContents', 'aggregatedContent', 'annotation', 'carouselContent', 'contextualDescription',
                        'contextualDescriptionV2', 'contextualHeader', 'dashEntityUrn', 'desktopPromoUpdate', 'detailHeader', 'footer',
                        'header', 'highlightedComments', 'interstitial', 'leadGenFormContent', 'leadGenFormContentV2',
                        'relatedContent', 'showSocialDetail', 'socialContent' ]

#=== FONCTIONS ====
def convert_epoch(epoch):
    # OBJECTIF : CONVERTIR EPOCH EN TEMPS UTC
    date_heure = datetime.datetime.utcfromtimestamp(epoch/1000)
    return(date_heure)

def get_post_id(linkedin_url):
    regex = r'([0-9]{19})'
    match = re.search(regex, linkedin_url)
    if match:
        post_id = match.group()
        return(post_id)
    return(None)

def extract_unix_timestamp(post_id):
    post_id_int = int(post_id)
    first_41_chars = bin(post_id_int)[2:43]
    timestamp = int(first_41_chars, 2)
    return(timestamp)

def unix_timestamp_to_human_date(timestamp):
    date_object = datetime.datetime.utcfromtimestamp(timestamp/1000)
    human_date_format = date_object.strftime('%Y-%m-%d %H:%M:%S UTC')
    return(human_date_format)

def create_json(data, sous_dossier, nom_fichier):
    # OBJECTIF = ARCHIVER LES DONNEES DANS UN FICHIER JSON
    path_to_file = sous_dossier + nom_fichier
    with open(path_to_file, 'w') as fp:
        json.dump(data, fp, sort_keys=True, default = json_converter)

def json_converter(o):
    # OBJECTIF : REPONDRE A CERTAIN PB DE MISE A JOUR DE JSON
    if isinstance(o, datetime.datetime):
        return o.__str__()

def recherche_meilleure_def(liste_artifacts):
    # OBJECTIF : RECUPERER DANS UNE LISTE LA MEILLEURE DEFINITION DE L'IMAGE (GENERALEMENT DANS UNE PARTIE ARTIFACTS)
    height_max = 0
    for k in liste_artifacts:
        if k['height'] > height_max:
            output = k['fileIdentifyingUrlPathSegment']
            height_max = k['height']
    return(output)

def recup_data(fichier_txt = '', fichier_json = ''):
    # OBJECTIF : FORMATER LES DONNEES DE LINKEDIN SOUS UN FORMAT JSON
    # Etape 1 : Préparation
    if fichier_txt == '':
        fichier_txt = linkedin_data_file
    if fichier_json == '':
        fichier_json = linkedin_json_file
    dict_linkedin_filtre = {}                                   # Fichier de sortie
    dict_linkedin_updatev2 ={}                                  # Dictionnaire des posts (thread des posts quand un post cite un autre)
    dict_linkedin_comment = {}                                  # Dictionnaire des commentaires
    dict_linkedin_profile = {}                                  # Dictionnaire des profils
    dict_linkedin_filtre['5_company'] = ''                      # Données de la compagnie de l'auteur du post
    dict_linkedin_filtre['6_group'] = ''                        # Données du groupe de l'auteur du post
    dict_linkedin_filtre['2_video'] = ''                        # Lien vers la vidéo, s'il y en a une
    list_linkedin_reaction = []                                 # Liste des réactions
    list_linkedin_socialactivity = []                           # Liste
    list_linkedin_autre = []                                    # Liste des cas non traités
    # Etape 2 : Récupération des données sous un format dictionnaire
    with open(dossier + fichier_txt, 'r') as fichier:
        all_content  = fichier.read()
        dict_linkedin= json.loads(all_content)
    # Etape 3 : Formatage des données
    list_included = dict_linkedin['included']
    for included in list_included:
        # Etape 3.1 : Données non prises en compte
        if 'FollowingInfo' in included['$type'] :
            continue
        elif 'SocialDetail' in included['$type'] : 
            continue
        elif 'Like' in included['$type'] : 
            continue
        elif 'SocialPermissions' in included['$type'] : 
            continue
        elif 'UpdateActions' in included['$type'] : 
            continue
        elif 'GroupMembership' in included['$type'] : 
            continue
        elif 'SaveAction' in included['$type'] :
            continue
        elif 'FeedMiniArticle' in included['$type'] :
            continue
        # Etape 3.2 : Données sur la compagnie de l'auteur du post
        elif 'MiniCompany' in included['$type'] :
            temp_dict_company = {'company_member_id': included['entityUrn'].split(':')[-1]}
            temp_dict_company['company_picture_url'] = included['logo']['rootUrl'] + recherche_meilleure_def(included['logo']['artifacts'])
            temp_dict_company['company_name'] = included['name']
            temp_dict_company['company_publicIdentifier'] = included['universalName']
            temp_dict_company['company_url'] = 'https://www.linkedin.com/company/' + quote(included['universalName'])
            dict_linkedin_filtre['5_company'] = temp_dict_company
        # Etape 3.3 : Liste des commentaires
        elif 'feed.Comment' in included['$type'] :
            temp_comment = {}
            list_keys = [x for x in list(included.keys()) if x not in filtre_comment]
            for key in list_keys:
                if key == 'comment':
                    liste_personne_citee = []
                    temp = included[key]['values']
                    for element in temp:
                        try:
                            temp_personne = {'pax_url': 'https://www.linkedin.com/in/' + element['*entity'].split(':')[-1], 'pax_value':element['value']}
                            liste_personne_citee.append(temp_personne)
                        except:
                            pass
                    temp_comment['personnes_citees'] = liste_personne_citee
                elif key == 'commentV2':
                    temp_comment['comments'] = included[key]['text']
                elif key == 'commenter':
                    temp_comment['commenter_member_id'] = included[key]['urn'].split(':')[-1]
                elif key == 'commenterForDashConversion':
                    temp_comment['author'] = included[key]['author']
                    temp_comment['commenter_publicIdentifier'] = included[key]['navigationUrl'].split('/')[-1]
                    temp_comment['commenter_url'] = included[key]['navigationUrl']
                    temp_comment['commenter_activity'] = included[key]['subtitle']
                    temp_comment['commenter_name'] = included[key]['title']['text']
                elif key == 'commenterProfileId':
                    temp_comment['commenter_profilId'] = included[key]      
                elif key == 'createdTime':
                    temp_comment['time_epoch'] = included[key]
                elif key == 'timeOffset':
                    temp_comment['time_offset'] = included[key]
                elif key == 'threadId':
                    temp_comment['post_id'] = included[key].split(':')[1]
                elif key == 'urn':
                    temp_comment['comment_id'] = included[key].split(',')[1].replace(')','')
                    temp_comment['time_datatime'] = convert_epoch(extract_unix_timestamp(temp_comment['comment_id']))
                else:
                    temp_comment[key] = included[key]
            dict_linkedin_comment[temp_comment['comment_id']] = temp_comment
        # Etape 3.4 : Recherche du lien vidéo (le cas échéant)
        elif 'VideoPlayMetadata' in included['$type'] :
            dict_linkedin_filtre['2_video'] = included['progressiveStreams'][0]['streamingLocations'][0]['url']
        # Etape 3.5 : Liste des profils ayant interagis
        elif 'MiniProfile' in included['$type'] :
            temp_profile = {'profile_profilId':included['entityUrn'].split(':')[-1]}
            temp_profile['profile_lastname'] = included['lastName']
            temp_profile['profile_firstname'] = included['firstName']
            temp_profile['profile_name'] = included['firstName'] + ' ' + included['lastName']
            temp_profile['profile_member_id'] = included['objectUrn'].split(':')[-1]
            temp_profile['profile_activity'] = included['occupation']
            try:
                url_profile = included['picture']['rootUrl'] + recherche_meilleure_def(included['picture']['artifacts'])
                temp_profile['profile_picture_url'] = url_profile
            except:
                temp_profile['profile_picture_url'] = ''
            temp_profile['profile_publicIdentifier'] = included['publicIdentifier']
            temp_profile['profile_url'] = 'https://www.linkedin.com/in/' + quote(included['publicIdentifier'])
            temp_profile['profile_trackingId'] = included['trackingId']
            dict_linkedin_profile[temp_profile['profile_member_id']] = temp_profile
        # Etape 3.6 : Liste des réactions
        elif 'Reaction' in included['$type'] :
            temp_reaction = {'reaction_profilId':included['actorUrn'].split(':')[-1]}
            temp_reaction['reaction_member_id'] = included['entityUrn'].split('member:')[1].split(',')[0]
            temp_reaction['reaction_post_id'] = included['entityUrn'].split(':')[-1].replace(')','')
            temp_reaction['reaction_name'] = included['name']['text']
            temp_reaction['reaction_url'] = included['navigationContext']['actionTarget']
            temp_reaction['reaction_organization'] = included['organizationActorUrn']
            temp_reaction['reaction_type'] = included['reactionType']
            list_linkedin_reaction.append(temp_reaction)
        # Etape 3.7 : Liste des types de réactions au post et aux commentaires
        elif 'SocialActivityCounts' in included['$type'] : 
            temp_comment = {'post_id':'', 'comment_id':''}
            if 'comment:' in included['entityUrn']:
                temp = included['entityUrn'].split('ugcPost:')[1].split(',')
                temp_comment['post_id'] = temp[0]
                temp_comment['comment_id'] = temp[1].replace(')','')
            elif 'Post:' in included['entityUrn']:
                temp_comment['post_id'] = included['entityUrn'].split('Post:')[1].split('-')[-1]
            dict_reaction = {}
            if len(included['reactionTypeCounts']) != 0:
                for element in included['reactionTypeCounts']:
                    dict_reaction[element['reactionType']] = element['count']
                temp_comment['reaction_type'] = dict_reaction
            else:
                temp_comment['reaction_type'] = {}
            list_linkedin_socialactivity.append(temp_comment)
        # Etape 3.8 : Liste de la série de post
        elif 'UpdateV2' in included['$type'] : 
            temp_updatev2 = {}
            list_keys_v2 = [x for x in list(included.keys()) if x not in filtre_comment2]
            for key in list_keys_v2:
                if key == '*socialDetail':
                    temp_updatev2['post_id'] = included[key].split(':')[-1].split('-')[-1]
                    temp_updatev2['time_datapost'] = convert_epoch(extract_unix_timestamp(temp_updatev2['post_id']))
                elif key == 'actor':
                    temp_updatev2['author_activity'] = included[key]['description']['text']
                    temp_updatev2['author_name'] = included[key]['name']['text']
                    temp_updatev2['author_url'] = included[key]['navigationContext']['actionTarget']
                    temp_updatev2['author_member_id'] = included[key]['urn'].split(':')[-1]
                elif key == 'commentary':
                    if str(included[key]) != 'None' :
                        temp_updatev2['post_message'] = included[key]['text']['text']
                        liste_hashtag = []
                        if 'attributes' in included[key]['text'].keys():
                            try:
                                if 'trackingUrn' in included[key]['text']['attributes'].keys():
                                    for hastag in included[key]['text']['attributes']:
                                        liste_hashtag.append(hastag['trackingUrn'].split(':')[-1])
                            except:
                                pass
                        temp_updatev2['post_hastag'] = liste_hashtag
                elif key == 'updateMetadata':
                    temp_updatev2['time_update'] = convert_epoch(extract_unix_timestamp(included[key]['urn'].split(':')[-1]))
                elif key == 'content':
                    if str(included['content']) != 'None':
                        if 'navigationContext' in included['content'].keys():
                            try:
                                temp_updatev2['media_exterieur_titre'] = included['content']['navigationContext']['accessibilityText']
                            except:
                                temp_updatev2['media_exterieur_titre'] = ''
                            try:
                                temp_updatev2['media_exterieur_lien'] = included['content']['navigationContext']['actionTarget']
                            except:
                                temp_updatev2['media_exterieur_lien'] = ''
                        if 'largeImage' in included['content'].keys():
                            try:
                                liste_image = []
                                for image in included['content']['largeImage']['attributes']:
                                    height = 0
                                    id_max = 0
                                    for k in range(len(image['vectorImage']['artifacts'])):
                                        if int(image['vectorImage']['artifacts'][k]['height']) > height:
                                            height = image['vectorImage']['artifacts'][k]['height']
                                            id_max = k
                                    liste_image.append(image['vectorImage']['rootUrl'] + image['vectorImage']['artifacts'][id_max]['fileIdentifyingUrlPathSegment'])
                                temp_updatev2['post_image_urls'] = liste_image
                                temp_updatev2['post_image_titre'] = included['content']['navigationContext']['accessibilityText']
                            except:
                                temp_updatev2['post_image'] = []
                        if 'images' in included['content'].keys():
                            liste_images = []
                            for image in included['content']['images']:
                                dict_image = {'img_text':image['accessibilityText']}
                                dict_image['img_url'] = image['attributes'][0]['vectorImage']['rootUrl'] + recherche_meilleure_def(image['attributes'][0]['vectorImage']['artifacts'])
                                liste_images.append(dict_image)
                            temp_updatev2['post_images'] = liste_images
                        # temp_updatev2[key] = included[key]
                else:
                    temp_updatev2[key] = included[key]
            dict_linkedin_updatev2[temp_updatev2['post_id']] = temp_updatev2
        # Etape 3.9 : Données sur le groupe
        elif 'MiniGroup' in included['$type'] :
            temp_group = {'group_description':included['groupDescription']}
            temp_group['group_id'] = included['entityUrn'].split(':')[-1]
            temp_group['group_name'] = included['groupName']
            temp_group['group_url'] = included['logo']['rootUrl'] + recherche_meilleure_def(included['logo']['artifacts'])
            dict_linkedin_filtre['6_group'] = temp_group
        else :
            list_linkedin_autre.append(included)
            print(included['$type'])
    # Etape 5: Ajout les stats de réactions dans les posts et commentaires
    for k in list_linkedin_socialactivity:
        if len(k['comment_id']) != 0 :
            dict_linkedin_comment[k['comment_id']]['reaction_type'] = k['reaction_type']
        elif len(k['post_id']) != 0 :
            dict_linkedin_updatev2[k['post_id']]['reaction_type'] = k['reaction_type']
    for k in list_linkedin_reaction:
        dict_linkedin_profile[k['reaction_member_id']]['reaction_type'] = k['reaction_type']
        dict_linkedin_profile[k['reaction_member_id']]['reaction_url'] = k['reaction_url']
        dict_linkedin_profile[k['reaction_member_id']]['profile_name'] = k['reaction_name']
    # Etape 6 : Concatenation
    dict_linkedin_filtre['3_comments'] = dict_linkedin_comment
    dict_linkedin_filtre['4_profile'] = dict_linkedin_profile
    dict_linkedin_filtre['1_post'] = dict_linkedin_updatev2
    dict_linkedin_filtre['autre_cas'] = list_linkedin_autre
    # Etape 7 : Enregistrement sous forme de json
    create_json(dict_linkedin_filtre, dossier, fichier_json)

#=== LANCEMENT ====
recup_data(fichier_txt = linkedin_data_file)