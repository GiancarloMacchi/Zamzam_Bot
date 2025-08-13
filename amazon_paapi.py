import logging
import bottlenose
from xml.dom import minidom

logger = logging.getLogger(__name__)

class AmazonApi:
    def __init__(self, access_key, secret_key, associate_tag, country):
        self.amazon = bottlenose.Amazon(
            AWSAccessKeyId=access_key,
            AWSSecretAccessKey=secret_key,
            AssociateTag=associate_tag,
            Region=country
        )

    def search_items(self, keywords, search_index="All", item_page=1):
        try:
            response = self.amazon.ItemSearch(
                Keywords=keywords,
                SearchIndex=search_index,
                ItemPage=str(item_page),
                ResponseGroup="Large"
            )
            return self.parse_response(response)
        except Exception as e:
            logger.error(f"❌ Errore Amazon API: {e}")
            return []

    def parse_response(self, xml_response):
        items = []
        try:
            dom = minidom.parseString(xml_response)
            for item_node in dom.getElementsByTagName("Item"):
                title_nodes = item_node.getElementsByTagName("Title")
                link_nodes = item_node.getElementsByTagName("DetailPageURL")
                
                title = title_nodes[0].firstChild.nodeValue if title_nodes else "Senza titolo"
                link = link_nodes[0].firstChild.nodeValue if link_nodes else ""

                items.append({
                    "title": title,
                    "link": link
                })
        except Exception as e:
            logger.error(f"❌ Errore parsing XML: {e}")
        return items
