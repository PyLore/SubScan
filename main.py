from concurrent.futures import ThreadPoolExecutor
from requests           import Session
from socket             import gethostbyname
from time               import time

from lib.constants import *
from lib.theme     import Colors
    
class SubScan(Session):
    """Module can be used for anything."""
    def __init__(self: object, domain: str = 'http://google.com') -> None:
        super().__init__() 
        
        self.domain_list: str = open('lib/subdomains.txt','r').read().splitlines()
         
        self._domain: str = domain
        
        self.results: list = []
        self.headers: dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}
    
    #############################################################
    """Property methods."""
    
    @property
    def domain(self: object) -> str:
        return self._domain
    

    @domain.setter
    def domain(self: object, domain: str) -> None:
        if not isinstance(domain, str):
            raise TypeError

        self._domain: str = self.check_url(domain)
        
    #############################################################
    """Static methods."""
    
    @staticmethod
    def check_url(domain: str) -> str:
        # Look for http(s)://www. and http(s)://
        for prefix in HTTP_PREFIXS:
            if f'{prefix}://www.' in domain:
                domain: str = domain.partition(f'{prefix}://www.')[2]
                
            elif f'{prefix}://' in domain:
                domain: str = domain.partition(f'{prefix}://')[2]
                
        if '/' in domain:
            domain: str = domain.partition('/')[0]
            
        return domain

    @staticmethod
    def _xd_get_status(status_code: int) -> str:
        # VERY PRIVATE METHOD NO ONE NEEDS TO USE LOL
        if str(status_code).startswith('4'):
           return f'{Colors.RED}{status_code}'
           
        if str(status_code).startswith('2'):
           return f'{Colors.LIME}{status_code}'
           
        return f'{Colors.RED}{status_code}'
           
    #############################################################
    """Main methods."""
    
    def check_domain(self: object, url: str) -> None:
        try:
            resp: object = self.get(
                url             = url,
                allow_redirects = True,
                timeout         = 5
            )
        except:
            return
        
        # Look for a 404 status code OR an error in the text response itself.
        if resp.status_code == 404 or [error for error in ERRORS if error in resp.text.lower()]:
            return
            
        data: dict = {
            'url'         : resp.url,
            'status_code' : resp.status_code,
            'ip_addr'     : gethostbyname(url.partition('//')[2])
        }
            
        if not data in self.results: 
            self.results.append(data)

  
    # Main function
    def get_results(self: object) -> None:
        self.results.clear()
        
        with ThreadPoolExecutor(max_workers=800) as executor:
            for sub_domain in self.domain_list:
                 for prefix in HTTP_PREFIXS:
                     executor.submit(
                          self.check_domain,
                          f"{prefix}://{sub_domain}.{self.domain}",
                     )
                     
                     
                                        
session: object = SubScan()
print(f'\x1bc{Colors.BANNER}')
if __name__ == '__main__':  
     while 1:
        session.domain: str = input(f'{Colors.WHITE}URL:{Colors.VIOLET} ')
        print(f'{Colors.WHITE}Finding subdomains...')
        
        # Check how long it takes to get all subdomains.
        start: int = time()
        session.get_results()
         
        if not session.results:
            print(f'{Colors.RED}• {Colors.WHITE}Failed to find any subdomains.\n')
            continue
        
        for res in session.results:    
            print(f' {Colors.VIOLET}• {session._xd_get_status(res["status_code"])} {Colors.WHITE}: {res["ip_addr"]:<15} : {res["url"]}')   
           
        print(f'\n{Colors.WHITE}Found {Colors.VIOLET}{len(session.results)} {Colors.WHITE}subdomains.')   
        print(f'{Colors.WHITE}Execution speed: {Colors.VIOLET}{time() - start} {Colors.WHITE}seconds.\n') 
