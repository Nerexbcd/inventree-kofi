from django.http import JsonResponse
from django.conf.urls import url

import json
from datetime import datetime as dt

# InvenTree plugin libs
from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UrlsMixin

from part.models import Part
from company.models import Company, Contact, Address
from order.models import SalesOrder, SalesOrderLineItem



# Plugin version number
from .version import PLUGIN_VERSION

class KofiPlugin(UrlsMixin, SettingsMixin, InvenTreePlugin):

    # plugin metadata for identity in InvenTree
    NAME = "KofiPlugin"
    SLUG = "kofi_plugin"
    TITLE = ("InvenTree Kofi Integration")
    DESCRIPTION = ("Integrates Your Ko-fi shop with InvenTree")
    VERSION = PLUGIN_VERSION
    AUTHOR = "Abílio Páscoa"
    WEBSITE = "https://github.com/Nerexbcd/inventree-kofi"

    # Plugin settings
    SETTINGS = {
        "ACTIVE": {
            "name": "Active",
            "description": "Ko-fi Integration is active",
            "validator": bool,
            "default": True,
        },
        "KOFI_TOKEN": {
            "name": "KOFI API TOKEN",
            "description": "Ko-fi API Token",
            "default": "",
        },
    }

    def add_contact(self, name, phone, email) -> int :
        company = Company.objects.filter(name="Ko-fi").first().id

        contact = Contact.objects.filter(email=email,company=company).first()
        if not contact:
            contact = Contact.objects.create(name=name, phone=phone, email=email, company=company, role="Customer")        
        return contact.id

    def add_address(self, email, shipping_info) -> int:
        company = Company.objects.filter(name="Ko-fi").first().id

        address = Address.objects.filter(company=company, email=email).first()
        if not address:
            address = Address.objects.create(
                company=company,
                title=email,
                line1=shipping_info["full_name"],
                line2=shipping_info["street_address"],
                postal_city=shipping_info["city"],
                state=shipping_info["state_or_province"],
                postcode=shipping_info["postal_code"],
                country=shipping_info["country"],
            )
        return address.id


    def receive(self, request):

        if not self.get_setting("ACTIVE"):
            return JsonResponse({"error": "Plugin is not active"}, status=400)

        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method"}, status=405)
        
        try:
            form_data = request.form.get("data")
            form_data = json.loads (form_data)
            res_token = form_data["verification_token"]
            timestamp = form_data["timestamp"]
            res_type = form_data["type"]
            user_name = form_data["from_name"]
            amount = form_data["amount"]
            email = form_data["email"]
            currency = form_data["currency"]
            shop_items = form_data["shop_items"]
            shipping = form_data["shipping"]
            phone = form_data["shipping"]["telephone"]
            reference = form_data["kofi_transaction_id"]
            
            # Validate token
            if res_token != self.get_setting("KOFI_TOKEN"):
                return ("Invalid token", 403)
            
            # Convert string to datetime
            datetime = dt.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
            date = datetime.strftime("%d/%m/%Y")
            time = datetime.strftime("%H:%M:%S")


            if res_type == "Shop Order":

                # Create list of product links

                contact = self.add_contact(user_name, phone, email)
                address = self.add_address(email, shipping)
                customer = Company.objects.filter(name="Ko-fi").first().id

                order = SalesOrder.objects.create(
                    customer_reference = reference,
                    customer_id = customer,
                    contact_id = contact,
                    address_id = address,
                    order_currency = currency,
                    creation_date = date,
                )


                for shop_item in shop_items:
                    

                    part = Part.objects.filter(IPN__iexact=shop_item['direct_link_code']).first()

                    
                    SalesOrderLineItem.objects.create(
                        quantity = shop_item['quantity'],
                        part_id = part.id,
                        order_id = order.id,
                        notes = shop_item['variation_name'],
                    )
                                                    
            return JsonResponse({"status": "success"}, status=200)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    # Plugin URLs
    def setup_urls(self):
        """URLs for app."""
        return [
            url(r"kofi/", self.receive, name="kofiWebhook"),
        ]