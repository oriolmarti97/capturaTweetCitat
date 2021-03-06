#Bot de twitter per fer captura de pantalla al tweet citat
#(english license below)
#Copyright (C) 2019  Oriol Martí i Rodríguez

#Aquest programa és lliure; el podeu redistribuir i/o modificar
# d'acord amb els termes de la Llicència pública general de GNU tal 
# i com la publica la Free Software Foundation; tant se val la versió 3
# de la Llicència com (si ho preferiu) qualsevol versió posterior.


#Aquest programa es distribueix amb l'esperança que serà útil, 
#però SENSE CAP GARANTIA; ni tant sols amb la garantia de 
#COMERCIALITZABILITAT O APTITUD PER A PROPÒSITS DETERMINATS.  Vegeu
#la Llicència general pública de GNU per a més detalls. 


#Hauríeu d'haver rebut una còpia de la llicència pública general 
#de GNU amb aquest programa; si no, consulteu https://www.gnu.org/licenses/



#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.
import tweepy
import os
#Per executar el bot cal tenir un arxiu key.py que declari les quatre variables amb els tokens donats per Twitter
from key import consumer_key, consumer_secret, access_token, access_token_secret
import random


auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)

api=tweepy.API(auth, wait_on_rate_limit=True)


jaCapturats=set()
delayCaptura=2000

def baixaIResponTweetB(idTweet, tweetARespondre):
    idTweet=str(idTweet)
    #Fem la captura
    alcada=600
    ruta='./temp/'+idTweet+'.png'
    url="https://twitter.com/CARREROBLANCO/status/%s"%idTweet
    os.system(f'xvfb-run cutycapt --url={url} --min-width=600 --min-height={alcada} --out={ruta} --delay={delayCaptura} 2>&1 >/dev/null')
    
    try:
        api.update_with_media(ruta,status='@%s'%tweetARespondre.user.screen_name,in_reply_to_status_id=tweetARespondre.id_str)
    except Exception as e:
        print(e)
        print('No he pogut respondre al tweet')

    os.remove(ruta)


def baixaIResponTweet(tweetABaixar, tweetARespondre):
    #Fem la captura
    if not hasattr(tweetABaixar,'media') or tweetABaixar.media is None:
        alcada=600
    else:
        alcada=1200
    ruta='./temp/'+tweetABaixar.id_str+'.png'
    url="https://twitter.com/%s/status/%s"%(tweetABaixar.user.screen_name,tweetABaixar.id_str)
    os.system(f'xvfb-run cutycapt --url={url} --min-width=600 --min-height={alcada} --out={ruta} --delay={delayCaptura} 2>&1 >/dev/null')
    
    try:
        api.update_with_media(ruta,status='@%s'%tweetARespondre.user.screen_name,in_reply_to_status_id=tweetARespondre.id_str)
    except Exception as e:
        print(e)
        print('No he pogut respondre al tweet')

    os.remove(ruta)

def respon_gatet(status):
    print('Gatet')
    api.update_with_media('gat trist.jpg',status='@%s :('%status.user.screen_name,in_reply_to_status_id=status.id_str)

class ElMeuEscoltador(tweepy.StreamListener):
    def on_status(self, status):
        '''FALTA REFACTORITZAR'''
        global api
        serp = '\U0001F40D'
        if (serp in status.user.name or serp in status.user.description) and random.randint(1,10)==1:
            # Als serpientos, una de cada 10 vegades, se'ls respondrà amb un meme
            api.update_with_media('serpiento.jpg',status='@%s'%status.user.screen_name,in_reply_to_status_id=status.id_str)
            return
        #Si té aquest atribut, vol dir que el tweet respon a gent no mencionada explícitament al tweet. Com que podria ser que el bot fos un d'ells, comprovem si ho és (si algú respon a un tweet del bot no hem de fer captura)
        if hasattr(status,'display_text_range'):
            if '@citatbot' not in status.text[status.display_text_range[0]:].lower():
                return
        if hasattr(status,'retweeted_status'):
            return
        if status.in_reply_to_status_id is None:
            #Ni tan sols respon a ningú
            api.update_with_media('gat saludant.jpg',status='@%s Hola :D'%status.user.screen_name,in_reply_to_status_id=status.id_str)
            return
        api.create_favorite(status.id)
        if status.id_str in jaCapturats:
            return
        jaCapturats.add(status.id_str)
        try:
            status_replied=api.get_status(status.in_reply_to_status_id)
        except Exception as e:
            print(e)
            respon_gatet(status)
            return
        if not hasattr(status_replied,'quoted_status_id') or status_replied.quoted_status_id is None:
            if not hasattr(status_replied,'in_reply_to_status_id') or status_replied.in_reply_to_status_id is None:
                #El tweet al que respon no cita ni respon a ningú. Com que hi ha respost, el veu, de manera que no cal captura
                respon_gatet(status)
                return
            try:
                citat=api.get_status(status_replied.in_reply_to_status_id)
                baixaIResponTweet(citat,status)
            except:
                try:
                    baixaIResponTweetB(status_replied.quoted_status_id,status)
                except Exception as e:
                    print(e)
                    respon_gatet(status)
                return
        else:
            try:
                citat=api.get_status(status_replied.quoted_status_id)
                baixaIResponTweet(citat,status)
            except:
                try:
                    baixaIResponTweetB(status_replied.quoted_status_id,status)
                    pass
                except Exception as e:
                    respon_gatet(status)
                return
    def on_data(self,data):
        super().on_data(data)
        if 'direct_message' in data:
            print('MD :D')
            print(data)
    def on_direct_message(self,status):
        print(status) #Falta implementar-ho. La idea és poder interactuar també per privat
        






escoltador=ElMeuEscoltador()
stream=tweepy.Stream(auth=api.auth,listener=escoltador)
stream.filter(track=['CitatBot'])
