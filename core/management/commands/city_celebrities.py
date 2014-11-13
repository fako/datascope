import json

from django.core.management.base import BaseCommand

from core.helpers.storage import get_hif_model
from core.helpers.enums import ProcessStatus


class Command(BaseCommand):
    """
    Clears TextStorage and/or ProcessStorage from the database.
    """

    def handle(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        self.args = "<city_name>/<lat>|<lon> <city_name>/<lat>|<lon> ..."

        # Import models here to prevent circular imports
        from core.processes.places import CityCelebrities
        from core.processes.base import Retrieve
        from core.output.http.services.manifests import CityCelebritiesService


        if not args:
            print("You'll need to specify coordinates like: London/51.5286416|-0.1015987")
            return

        for arg in args:

            # Start the process
            city, coords = arg.split('/')
            print("Fetching information for: {} at {}".format(city, coords))
            city_celebrities = CityCelebrities()
            city_celebrities.execute(coords=coords)

            # Finish the process synchronously
            city_celebrities.task.get()
            city_celebrities.execute(coords=coords)

            if city_celebrities.status != ProcessStatus.DONE:
                print("City Celebrities process failed with: {}".format(city_celebrities.status))
                return

            print("Fetching claims information for all backlinks of locations")

            locations = []
            for location in city_celebrities.rsl:

                if "backlinks" not in location:
                    print("Skipping location due to lack of backlinks: " + location['title'])
                    continue

                print("Next up location: " + location['title'])
                human = {
                    "property": "P31",
                    "item": 5
                }
                people = []
                for page in location['backlinks']:
                    retriever = Retrieve()
                    retriever.execute(page['wikidata'], _link="WikiDataClaims", excluded_properties=[])

                    if retriever.status != ProcessStatus.DONE:
                        print("Skipping due to failed retriever: " + location['title'])
                        continue

                    claims = retriever.rsl

                    if human not in claims:
                        print("Backlink is not human: " + page['title'])
                        continue

                    print("Adding backlink to people set: " + page['title'])
                    page['claims'] = claims
                    people.append(page)

                if not people:
                    print("Skipping location due to lack of people backlinks: " + location['title'])
                    continue

                location['people'] = people
                del(location['backlinks'])
                locations.append(location)

            cc_service = CityCelebritiesService()
            cc_service.setup({"query": city})
            cc_service.content = locations
            cc_service.retain()


# Locations: 352
# People: 9676
# City University London = 152
# International Society for Soil Mechanics and Geotechnical Engineering = 3
# Northampton Square = 2
# City Road = 12
# Boxing at the 1908 Summer Olympics = 11
# Spa Green Estate = 2
# City Law School = 16
# Clerkenwell = 110
# Finsbury = 52
# Finsbury Estate = 2
# Angel tube station = 2
# Urdang Academy = 1
# Metropolitan Borough of Finsbury = 11
# Victoria Miro Gallery = 76
# Slimelight = 3
# Angel, London = 1
# Centre for Economic Policy Research = 58
# Ironmonger Row Baths = 1
# Berry Street Studio = 3
# Red Bull Theatre = 25
# New Prison = 7
# Spa Fields = 8
# Cubitt Artists = 4
# Clerkenwell explosion = 3
# Clerkenwell Prison = 5
# St James's Church, Clerkenwell = 8
# St Luke Old Street = 9
# Finsbury Health Centre = 3
# Clerkenwell Priory = 7
# Academy of St Martin in the Fields = 58
# Golden Lane, London = 3
# Clerkenwell Road = 4
# O2 Academy Islington = 3
# St Luke's = 9
# Maison Novelli = 2
# Middlesex Sessions House = 1
# The Children's Society = 15
# St John's Gate, Clerkenwell = 2
# Italia Conti Academy of Theatre Arts = 84
# Article 19 = 12
# Trade (nightclub) = 4
# Turnmills = 13
# The Antique Wine Company = 1
# Statue of Hugh Myddelton, Islington Green = 2
# Fann Street = 4
# Fann Street Foundry = 5
# London Charterhouse = 68
# Moorfields Eye Hospital = 37
# Golden Lane Estate = 2
# Bevin Court = 2
# Royal Agricultural Hall = 5
# Drama Centre London = 80
# Islington Green = 2
# Coldbath Fields Prison = 10
# White Conduit Fields = 7
# Riceyman Steps = 1
# Hicks Hall = 3
# St Peter's Italian Church = 1
# City of London Academy, Islington = 2
# Charterhouse Square = 16
# Whitecross Street, London = 6
# Turnmill Street = 2
# The Farmiloe Building = 1
# St Luke's Hospital for Lunatics = 7
# Elizabeth Garrett Anderson School = 2
# Fox and Anchor = 1
# St. John (restaurant) = 1
# Pentonville = 44
# L-13 Light Industrial Workshop = 1
# The Aquarium L-13 = 2
# London Fever Hospital = 8
# London Lesbian and Gay Centre = 2
# Farringdon Road = 6
# Barbican tube station = 2
# Farringdon station = 1
# Saffron Hill = 6
# Fabric (club) = 51
# East London Tech City = 3
# Bunhill Fields = 131
# Hatton Garden = 44
# Charterhouse Street = 1
# Smithfield, London = 97
# Cass Business School = 51
# Islington South and Finsbury (UK Parliament constituency) = 9
# Church Missionary Society College, Islington = 6
# St Mary's Church, Islington = 27
# St Bartholomew-the-Great = 21
# Cloth Fair = 1
# Gray's Inn Road = 27
# Leather Lane = 4
# Rutland House = 2
# Honourable Artillery Company Museum = 1
# New Road, London = 3
# UK Financial Investments = 32
# London Welsh Centre = 16
# Eastman Dental Hospital = 9
# Bartholomew Fair = 18
# Bloomsbury = 141
# St Pancras, London = 163
# Wesley's Chapel = 12
# City of London School for Girls = 23
# Artillery Ground = 74
# Silk Street, London = 1
# Ely Place = 10
# Barbican Estate = 26
# Charles Dickens Museum = 16
# St Etheldreda's Church = 6
# Grub Street = 28
# Chiswell Street = 4
# Gainsborough Pictures = 54
# St Bartholomew-the-Less = 9
# Cripplegate = 58
# Doughty Street = 9
# Occupy London = 10
# Shoreditch Park = 1
# Guildhall School of Music and Drama = 385
# Royal National Throat, Nose and Ear Hospital = 9
# St Giles-without-Cripplegate = 29
# School of Community and Health Sciences = 1
# Goodenough College = 14
# Holborn Bars = 1
# St Bartholomew's Hospital = 198
# Gray's Inn = 373
# Museum of London = 51
# Mecklenburgh Square = 4
# Wikimedia UK = 2
# St John the Baptist, Hoxton = 1
# Portpool = 2
# Hoxton = 134
# Holborn Circus = 1
# Holborn Viaduct = 13
# The Poor School = 16
# Furnival's Inn = 21
# Upper Street = 3
# All Visual Arts = 4
# St Andrew, Holborn = 36
# Little Britain, London = 16
# Monkwell Square = 1
# St Sepulchre-without-Newgate = 31
# Giltspur Street = 2
# St Olave Silver Street = 4
# Aldersgate = 42
# St Sepulchre (parish) = 3
# St Botolph's Aldersgate = 6
# Barnard's Inn = 15
# Old Street = 13
# Postman's Park = 4
# Scala (club) = 16
# Giltspur Street Compter = 3
# Chancery Lane tube station = 1
# 125 London Wall = 24
# Sainsbury's = 46
# London School of Business and Finance = 4
# Finsbury Square = 17
# Gresham College = 167
# London Borough of Hackney = 152
# The People's Supermarket = 3
# Rotherfield Primary School = 1
# Fore Street, London = 4
# St Alphage London Wall = 5
# Sartorial Contemporary Art = 5
# Lamb's Conduit Street = 6
# Greyfriars, London = 19
# Finsbury Pavement = 1
# Bell Pottinger Private = 1
# Theobald's Road = 5
# Oat Lane = 1
# General Post Office, London = 3
# St Martin's Le Grand = 1
# St Mary Staining = 2
# St Anne and St Agnes = 7
# Hoxton Square = 29
# 20 Hoxton Square = 4
# Farringdon Market = 2
# Fleet Prison = 209
# Fleet Market = 3
# Rosemary Branch Theatre = 6
# Center for Transnational Legal Studies = 2
# Old Bailey = 155
# Nesta (charity) = 3
# Moorgate station = 2
# Christ Church Greyfriars = 20
# St Alban, Wood Street = 7
# Stuckism International Gallery = 40
# Newgate Prison = 211
# Metropolitan Borough of Islington = 7
# The Prince's Drawing School = 5
# The Prince's School of Traditional Arts = 3
# St John Zachary = 2
# Chartered Quality Institute = 3
# International Hall, London = 2
# Great Ormond Street Hospital = 180
# Powis House = 1
# Moor House = 1
# Carl Freedman Gallery = 9
# London Silver Vaults = 1
# Moorfields = 52
# St Nicholas Shambles = 2
# BT Centre = 1
# St Mary Aldermanbury = 19
# Wood Street, London = 5
# Moorgate tube crash = 3
# Clockmakers' Museum = 4
# Battlebridge Basin = 1
# Bassishaw = 10
# London Stock Exchange Group = 4
# Goldsmiths' Hall = 7
# St Michael Bassishaw = 4
# Foster Lane = 8
# London King's Cross railway station = 10
# Conway Hall Ethical Society = 10
# London Guildhall University = 42
# St Michael Wood Street = 3
# Brunswick Square = 12
# Electra House = 2
# Moorgate = 5
# Kings Cross, London = 57
# St Leonard, Foster Lane = 1
# London School of Medicine for Women = 37
# Newgate = 67
# Holywell Priory = 6
# St Mary Moorfields = 3
# King's Cross fire = 6
# 88 Wood Street = 1
# Paternoster Square = 11
# Rivington Place = 4
# Stuart Hall Library = 1
# The Theatre = 13
# Chancery Lane = 59
# Lincoln's Inn = 410
# Coleman Street = 13
# Guildhall, London = 100
# St. Paul's tube station = 3
# King's Cross St. Pancras tube station = 3
# Paternoster Row = 36
# BT Archives = 1
# Wood Street Compter = 3
# St Vedast Foster Lane = 13
# Hackney College = 8
# Royal London Hospital for Integrated Medicine = 7
# National Hospital for Neurology and Neurosurgery = 52
# Amen Corner, London = 2
# Guildhall Library = 14
# Great Fire of London = 100
# University of the Arts London = 108
# Association of Chartered Certified Accountants = 27
# Gresham Street = 3
# Finsbury Circus = 12
# County of London = 92
# Ave Maria Lane = 1
# Maughan Library = 7
# Queen Square, London = 44
# Daily Express Building, London = 38
# Red Lion Square = 19
# Fetter Lane = 32
# Basinghall Street = 10
# Bell Savage Inn = 2
# Bread Street = 18
# Poetry Bookshop = 5
# Ludgate Circus = 1
# Ludgate = 29
# St Lawrence Jewry = 21
# Guildhall Art Gallery = 34
# Hope and Anchor, Islington = 3
# St Martin, Ludgate = 7
# Occupy Berlin = 2
# St Pancras railway station = 12
# Cheap (ward) = 10
# Churchill House = 1
# St Paul's Cross = 83
# King's Cross railway accident = 1
# Brunswick Centre = 3
# Old Devonshire House = 2
# Curtain Theatre = 11
# Ye Olde Cheshire Cheese = 1
# Mayor's and City of London Court = 7
# St. Pancras Renaissance London Hotel = 4
# October Gallery = 9
# St Peter, Westcheap = 2
# Broadgate = 14
# Liberty of the Rolls = 1
# New College of the Humanities = 22
# Camden Town Hall = 1
# St. Stephen Coleman Street = 2
# Shoreditch = 105
# Paul's walk = 62
# Ludgate Hill = 37
# Diocese of London = 215
# Domus Conversorum = 2
# Sir John Soane's Museum = 57
# St Bride's Church = 45
# All Hallows Honey Lane = 3
# Dorset Garden Theatre = 7
# St George the Martyr, Holborn = 1
# Finsbury Chapel = 5
# College of Minor Canons = 62
# Old St Paul's Cathedral = 113
# St Paul's Cathedral = 169
# Masters (snooker) = 84
# Russell Square tube station = 7
# Estorick Collection of Modern Italian Art = 2
# St Leonard's, Shoreditch = 23
# Shoreditch (parish) = 4
# St Bride Library = 5
# UK Sport = 34
# Horse Hospital = 5
# Cheapside = 114
# German Gymnasium, London = 3
# St Dunstan-in-the-West = 32
# Central School of Art and Design = 119
# Grantham Research Institute on Climate Change and the Environment = 15
# One New Change = 5
# Islington = 192
# Holborn = 119
# Commonwealth Hall = 2
# St Augustine Watling Street = 5
# Clifford's Inn = 25
# St Matthew Friday Street = 2
# St Olave Old Jewry = 4
# St Mary-le-Bow = 18
# Salisbury Court Theatre = 17
# Southampton Row = 15
# Lincoln's Inn Fields = 164
# Serjeant's Inn = 12
# Hughes Parry Hall, London = 2
# Shoreditch High Street = 3
# Broadgate Tower = 2
# Castle Baynard = 7
# Howard Griffin Gallery = 5
# Liverpool Road = 2
# Metropolitan Borough of Shoreditch = 2
# India Office Records = 9
# High Holborn = 29
# Cotton library = 35
# Old Jewry = 11
# Prince Henry's Room = 1
# Lothbury = 25
# Lisle's Tennis Court = 23
# National Firefighters Memorial = 3
# Blackfriars Theatre = 40
# Russell Institution = 9
# Hospital of St Thomas of Acre = 8
# St. Mary Magdalen, Milk Street = 10
# Alsatia = 2
# 21 July 2005 London bombings = 45
# Royal College of Surgeons of England = 330
# Faculty of General Dental Practice = 1
# St Margaret Lothbury = 6
# ATC Theatre = 3
# All Hallows, Bread Street = 8
# Norton Folgate = 4
# Geffrye Museum = 23

