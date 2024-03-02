import shopify

API_KEY = "01cfa8da6db49cd6a7988357e8922257"
API_SECRET = "9dd17e070c14c6a83005c4977fc25ccb"
Admin_API_ACCESS_TOKEN = "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"
SHOP_URL = "https://quickstart-d7f6d956.myshopify.com/admin/api/2023-07"

shopify.ShopifyResource.set_site(SHOP_URL)
shopify.ShopifyResource.headers = {'X-Shopify-Access-Token': Admin_API_ACCESS_TOKEN}

new_product = shopify.Product()
variant = shopify.Variant()

variant.metafields = [
    {
        "key": "date_of_selling",
        "value": 12354,
        "value_type": "string",
        "namespace": "date"
    }
]
new_product.variants = [variant]
new_product.save()