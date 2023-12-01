import subprocess
import frappe
import requests
import datetime
import json
import os
import base64
from frappe import _
from frappe.core.doctype.file.file import attach_files_to_document
import qrcode


invoice_template = """ 
            <?xml version="1.0" encoding="UTF-8"?>
            <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
                
                
                <cbc:ProfileID>reporting:1.0</cbc:ProfileID>
                <cbc:ID>SME00023</cbc:ID>
                <cbc:UUID>8d487816-70b8-4ade-a618-9d620b73814a</cbc:UUID>
                <cbc:IssueDate>{posting_date}</cbc:IssueDate>
                <cbc:IssueTime>{posting_time}</cbc:IssueTime>
                <cbc:InvoiceTypeCode name="0100000">388</cbc:InvoiceTypeCode>
                <cbc:DocumentCurrencyCode>SAR</cbc:DocumentCurrencyCode>
                <cbc:TaxCurrencyCode>SAR</cbc:TaxCurrencyCode>
                <cac:AdditionalDocumentReference>
                    <cbc:ID>ICV</cbc:ID>
                    <cbc:UUID>23</cbc:UUID>
                </cac:AdditionalDocumentReference>
                <cac:AdditionalDocumentReference>
                    <cbc:ID>PIH</cbc:ID>
                    <cac:Attachment>
                        <cbc:EmbeddedDocumentBinaryObject mimeCode="text/plain">NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ==</cbc:EmbeddedDocumentBinaryObject>
                    </cac:Attachment>
                </cac:AdditionalDocumentReference>
                <cac:AccountingSupplierParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID schemeID="CRN">311111111111113</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PostalAddress>
                            <cbc:StreetName>الامير سلطان</cbc:StreetName>
                            <cbc:BuildingNumber>2322</cbc:BuildingNumber>
                            <cbc:PlotIdentification>2223</cbc:PlotIdentification>
                            <cbc:CitySubdivisionName>الرياض</cbc:CitySubdivisionName>
                            <cbc:CityName>الرياض | Riyadh</cbc:CityName>
                            <cbc:PostalZone>23333</cbc:PostalZone>
                            <cac:Country>
                                <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                                <cbc:CompanyID>300075588700003</cbc:CompanyID>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>Acme Widget’s LTD</cbc:RegistrationName>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingSupplierParty>
                <cac:AccountingCustomerParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID schemeID="NAT">{customer_tax_id}</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PostalAddress>
                            <cbc:StreetName>{street}</cbc:StreetName>
                            <cbc:BuildingNumber>{building}</cbc:BuildingNumber>
                            <cbc:PlotIdentification>{plot}</cbc:PlotIdentification>
                            <cbc:CitySubdivisionName>{subdivission}</cbc:CitySubdivisionName>
                            <cbc:CityName>{city}</cbc:CityName>
                            <cbc:PostalZone>{postal_code}</cbc:PostalZone>
                            
                            <cac:Country>
                                <cbc:IdentificationCode>{country}</cbc:IdentificationCode>
                            </cac:Country>
                        </cac:PostalAddress>
                        <cac:PartyTaxScheme>
                            <cac:TaxScheme>
                                <cbc:ID>VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:PartyTaxScheme>
                        <cac:PartyLegalEntity>
                            <cbc:RegistrationName>{customer_name}</cbc:RegistrationName>
                        </cac:PartyLegalEntity>
                    </cac:Party>
                </cac:AccountingCustomerParty>
                <cac:Delivery>
                    <cbc:ActualDeliveryDate>{delivery_date}</cbc:ActualDeliveryDate>
                </cac:Delivery>
                <cac:PaymentMeans>
                    <cbc:PaymentMeansCode>{payment_mode_code}</cbc:PaymentMeansCode>
                </cac:PaymentMeans>
                {invoice_level_discount}
                <cac:TaxTotal>
                    <cbc:TaxAmount currencyID="SAR">{base_net_total_taxes_and_charges}</cbc:TaxAmount>
                </cac:TaxTotal>
                <cac:TaxTotal>
                    <cbc:TaxAmount currencyID="SAR">{total_taxes_and_charges}</cbc:TaxAmount>
                    <cac:TaxSubtotal>
                        <cbc:TaxableAmount currencyID="SAR">{taxable_amount}</cbc:TaxableAmount>
                        <cbc:TaxAmount currencyID="SAR">{sub_total_taxes_and_charges}</cbc:TaxAmount>
                        <cac:TaxCategory>
                            <cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">S</cbc:ID>
                            <cbc:Percent>{tax_percentage}</cbc:Percent>
                            <cac:TaxScheme>
                            <cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>
                            </cac:TaxScheme>
                        </cac:TaxCategory>
                    </cac:TaxSubtotal>
                </cac:TaxTotal>
                <cac:LegalMonetaryTotal>
                    <cbc:LineExtensionAmount currencyID="SAR">{base_net_total}</cbc:LineExtensionAmount>
                    <cbc:TaxExclusiveAmount currencyID="SAR">{net_total}</cbc:TaxExclusiveAmount>
                    <cbc:TaxInclusiveAmount currencyID="SAR">{grand_total}</cbc:TaxInclusiveAmount>
                    <cbc:AllowanceTotalAmount currencyID="SAR">{total_discount}</cbc:AllowanceTotalAmount>
                    <cbc:PrepaidAmount currencyID="SAR">{prepaid_amount}</cbc:PrepaidAmount>
                    <cbc:PayableAmount currencyID="SAR">{outstanding_amount}</cbc:PayableAmount>
                </cac:LegalMonetaryTotal>
            {items}
            </Invoice>
"""


invoice_level_discount_template  ="""
                  <cac:AllowanceCharge>
                    <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
                    <cbc:AllowanceChargeReason>discount</cbc:AllowanceChargeReason>
                    <cbc:Amount currencyID="SAR">{discount_amount}</cbc:Amount>
                    <cac:TaxCategory>
                        <cbc:ID schemeID="UN/ECE 5305" schemeAgencyID="6">S</cbc:ID>
                        <cbc:Percent>{tax_percentage}</cbc:Percent>
                        <cac:TaxScheme>
                            <cbc:ID schemeID="UN/ECE 5153" schemeAgencyID="6">VAT</cbc:ID>
                        </cac:TaxScheme>
                    </cac:TaxCategory>
                </cac:AllowanceCharge>
 """

items_template = """ 
    <cac:InvoiceLine>
            <cbc:ID>{idx}</cbc:ID>
            <cbc:InvoicedQuantity unitCode="PCE">{qty}</cbc:InvoicedQuantity>
            <cbc:LineExtensionAmount currencyID="SAR">{amount}</cbc:LineExtensionAmount>
            <cac:TaxTotal>
                <cbc:TaxAmount currencyID="SAR">{tax_amount}</cbc:TaxAmount>
                <cbc:RoundingAmount currencyID="SAR">{rounding_amount}</cbc:RoundingAmount>
            </cac:TaxTotal>
            <cac:Item>
                <cbc:Name>{item_name}</cbc:Name>
                <cac:ClassifiedTaxCategory>
                    <cbc:ID>{tax_category}</cbc:ID>
                    <cbc:Percent>{tax_percentage}</cbc:Percent>
                    <cac:TaxScheme>
                        <cbc:ID>VAT</cbc:ID>
                    </cac:TaxScheme>
                </cac:ClassifiedTaxCategory>
            </cac:Item>
            <cac:Price>
                <cbc:PriceAmount currencyID="SAR">{rate}</cbc:PriceAmount>
                <cac:AllowanceCharge>
                <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
                <cbc:AllowanceChargeReason>discount</cbc:AllowanceChargeReason>
                <cbc:Amount currencyID="SAR">{discount_amount}</cbc:Amount>
                </cac:AllowanceCharge>
            </cac:Price>
        </cac:InvoiceLine>  
 """

@frappe.whitelist()
def sign_invoice(docname):
    zatca_settings = frappe.get_single('ZATCA Settings')
    if not zatca_settings.enable_zatca:
        frappe.msgprint("PLease enable ZATCA settings")
        return False
    file_path =  zatca_settings.path_for_zatca_files+docname+".xml"
    sign_invoice_path = zatca_settings.path_for_zatca_files+docname+"_signed.xml"
    sign_api_path =  zatca_settings.path_for_zatca_files+docname+"_api.json"
    with open(file_path, "w", encoding="utf-8") as f:
        invoice_xml_string = get_invoice_xml_string(docname)
        f.write(invoice_xml_string.strip())
        f.close()
        try:
            my_env = {**os.environ, 
            'FATOORA_HOME': zatca_settings.zatca_sdk_root_path+'Apps',
            'SDK_CONFIG': zatca_settings.zatca_sdk_root_path+'Configuration/config.json', 
            'PATH': zatca_settings.zatca_sdk_root_path+'Apps/:'+zatca_settings.zatca_sdk_root_path+'Apps/' + os.environ['PATH']}
            
            temp = subprocess.Popen("fatoora -sign -invoice {0} -signedInvoice {1}".format(file_path,sign_invoice_path),
              stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,env=my_env
            )
            temp.wait()
            output = str(temp.communicate())
            #frappe.msgprint(str(output))
            subprocess.Popen("rm {0}".format(file_path),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
            
            temp = subprocess.Popen("fatoora -invoice {0} -invoiceRequest -apiRequest {1}".format(sign_invoice_path,sign_api_path),
              stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,env=my_env
            )
            temp.wait()
            doc = frappe.get_doc("Sales Invoice",docname)
            path_components = sign_invoice_path.split("/private")
            file_path = "/private"+path_components[-1]
            doc.signed_file = file_path
            doc.signed=1
            doc.save()
            add_attachment(file_path,docname,"signed_file")
        except subprocess.CalledProcessError as e:
            frappe.msgprint("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            return False
        
        
    return True

@frappe.whitelist()
def report_invoice(docname):
    zatca_settings = frappe.get_single('ZATCA Settings')
    if not zatca_settings.enable_zatca:
        frappe.msgprint("PLease enable ZATCA settings")
        return False
    sign_api_path = zatca_settings.path_for_zatca_files+docname+"_api.json"
    with open(sign_api_path, "r", encoding="utf-8") as f:
        payload = f.read()
        payload = payload.encode()
        print(payload)
        response = requests.post(
            url= zatca_settings.api_end_point+"reporting/single",
            headers={
                'accept': 'application/json',
                'accept-language': 'en',
                'Clearance-Status': '0',
                'Accept-Version': 'V2',
                'Authorization': 'Basic VFVsSlJERkVRME5CTTIxblFYZEpRa0ZuU1ZSaWQwRkJaVE5WUVZsV1ZUTTBTUzhyTlZGQlFrRkJRamRrVkVGTFFtZG5jV2hyYWs5UVVWRkVRV3BDYWsxU1ZYZEZkMWxMUTFwSmJXbGFVSGxNUjFGQ1IxSlpSbUpIT1dwWlYzZDRSWHBCVWtKbmIwcHJhV0ZLYXk5SmMxcEJSVnBHWjA1dVlqTlplRVo2UVZaQ1oyOUthMmxoU21zdlNYTmFRVVZhUm1ka2JHVklVbTVaV0hBd1RWSjNkMGRuV1VSV1VWRkVSWGhPVlZVeGNFWlRWVFZYVkRCc1JGSlRNVlJrVjBwRVVWTXdlRTFDTkZoRVZFbDVUVVJaZUUxcVJUTk9SRUV4VFd4dldFUlVTVEJOUkZsNFRWUkZNMDVFUVRGTmJHOTNVMVJGVEUxQmEwZEJNVlZGUW1oTlExVXdSWGhFYWtGTlFtZE9Wa0pCYjFSQ1YwWnVZVmQ0YkUxU1dYZEdRVmxFVmxGUlRFVjNNVzlaV0d4b1NVaHNhRm95YUhSaU0xWjVUVkpKZDBWQldVUldVVkZFUlhkcmVFMXFZM1ZOUXpSM1RHcEZkMVpxUVZGQ1oyTnhhR3RxVDFCUlNVSkNaMVZ5WjFGUlFVTm5Ua05CUVZSVVFVczViSEpVVm10dk9YSnJjVFphV1dOak9VaEVVbHBRTkdJNVV6UjZRVFJMYlRkWldFb3JjMjVVVm1oTWEzcFZNRWh6YlZOWU9WVnVPR3BFYUZKVVQwaEVTMkZtZERoREwzVjFWVms1TXpSMmRVMU9ielJKUTBwNlEwTkJhVTEzWjFsblIwRXhWV1JGVVZOQ1owUkNLM0JJZDNkbGFrVmlUVUpyUjBFeFZVVkNRWGRUVFZNeGIxbFliR2htUkVsMFRXcE5NR1pFVFhSTlZFVjVUVkk0ZDBoUldVdERXa2x0YVZwUWVVeEhVVUpCVVhkUVRYcEJkMDFFWXpGT1ZHYzBUbnBCZDAxRVFYcE5VVEIzUTNkWlJGWlJVVTFFUVZGNFRWUkJkMDFTUlhkRWQxbEVWbEZSWVVSQmFHRlpXRkpxV1ZOQmVFMXFSVmxOUWxsSFFURlZSVVIzZDFCU2JUbDJXa05DUTJSWVRucGhWelZzWXpOTmVrMUNNRWRCTVZWa1JHZFJWMEpDVTJkdFNWZEVObUpRWm1KaVMydHRWSGRQU2xKWWRrbGlTRGxJYWtGbVFtZE9Wa2hUVFVWSFJFRlhaMEpTTWxsSmVqZENjVU56V2pGak1XNWpLMkZ5UzJOeWJWUlhNVXg2UWs5Q1owNVdTRkk0UlZKNlFrWk5SVTluVVdGQkwyaHFNVzlrU0ZKM1QyazRkbVJJVGpCWk0wcHpURzV3YUdSSFRtaE1iV1IyWkdrMWVsbFRPVVJhV0Vvd1VsYzFlV0l5ZUhOTU1WSlVWMnRXU2xSc1dsQlRWVTVHVEZaT01WbHJUa0pNVkVWMVdUTktjMDFKUjNSQ1oyZHlRbWRGUmtKUlkwSkJVVk5DYjBSRFFtNVVRblZDWjJkeVFtZEZSa0pSWTNkQldWcHBZVWhTTUdORWIzWk1NMUo2WkVkT2VXSkROVFpaV0ZKcVdWTTFibUl6V1hWak1rVjJVVEpXZVdSRlZuVmpiVGx6WWtNNVZWVXhjRVpoVnpVeVlqSnNhbHBXVGtSUlZFVjFXbGhvTUZveVJqWmtRelZ1WWpOWmRXSkhPV3BaVjNobVZrWk9ZVkpWYkU5V2F6bEtVVEJWZEZVelZtbFJNRVYwVFZObmVFdFROV3BqYmxGM1MzZFpTVXQzV1VKQ1VWVklUVUZIUjBneWFEQmtTRUUyVEhrNU1HTXpVbXBqYlhkMVpXMUdNRmt5UlhWYU1qa3lURzVPYUV3eU9XcGpNMEYzUkdkWlJGWlNNRkJCVVVndlFrRlJSRUZuWlVGTlFqQkhRVEZWWkVwUlVWZE5RbEZIUTBOelIwRlJWVVpDZDAxRFFtZG5ja0puUlVaQ1VXTkVRWHBCYmtKbmEzSkNaMFZGUVZsSk0wWlJiMFZIYWtGWlRVRnZSME5EYzBkQlVWVkdRbmROUTAxQmIwZERRM05IUVZGVlJrSjNUVVJOUVc5SFEwTnhSMU5OTkRsQ1FVMURRVEJyUVUxRldVTkpVVU5XZDBSTlkzRTJVRThyVFdOdGMwSllWWG92ZGpGSFpHaEhjRGR5Y1ZOaE1rRjRWRXRUZGpnek9FbEJTV2hCVDBKT1JFSjBPU3N6UkZOc2FXcHZWbVo0ZW5Ka1JHZzFNamhYUXpNM2MyMUZaRzlIVjFaeVUzQkhNUT09OlhsajE1THlNQ2dTQzY2T2JuRU8vcVZQZmhTYnMza0RUalduR2hlWWhmU3M9',
                'Content-Type': 'application/json'
            },
            data=payload
        )
        frappe.msgprint(str(response.text))
        if response.status_code == 200:
            doc = frappe.get_doc("Sales Invoice",docname)
            doc.reported=1
            doc.save()
            return True
        return False

@frappe.whitelist()
def clear_invoice(docname):
    zatca_settings = frappe.get_single('ZATCA Settings')
    if not zatca_settings.enable_zatca:
        frappe.msgprint("PLease enable ZATCA settings")
        return False
    sign_api_path = zatca_settings.path_for_zatca_files+docname+"_api.json"
    cleared_invoice_path = zatca_settings.path_for_zatca_files+docname+"_cleared.json"
    with open(sign_api_path, "r", encoding="utf-8") as f:
        payload = f.read()
        payload = payload.encode()
        print(payload)
        response = requests.post(
            url= zatca_settings.api_end_point+"clearance/single",
            headers={
                'accept': 'application/json',
                'accept-language': 'en',
                'Clearance-Status': '1',
                'Accept-Version': 'V2',
                'Authorization': 'Basic VFVsSlJERkVRME5CTTIxblFYZEpRa0ZuU1ZSaWQwRkJaVE5WUVZsV1ZUTTBTUzhyTlZGQlFrRkJRamRrVkVGTFFtZG5jV2hyYWs5UVVWRkVRV3BDYWsxU1ZYZEZkMWxMUTFwSmJXbGFVSGxNUjFGQ1IxSlpSbUpIT1dwWlYzZDRSWHBCVWtKbmIwcHJhV0ZLYXk5SmMxcEJSVnBHWjA1dVlqTlplRVo2UVZaQ1oyOUthMmxoU21zdlNYTmFRVVZhUm1ka2JHVklVbTVaV0hBd1RWSjNkMGRuV1VSV1VWRkVSWGhPVlZVeGNFWlRWVFZYVkRCc1JGSlRNVlJrVjBwRVVWTXdlRTFDTkZoRVZFbDVUVVJaZUUxcVJUTk9SRUV4VFd4dldFUlVTVEJOUkZsNFRWUkZNMDVFUVRGTmJHOTNVMVJGVEUxQmEwZEJNVlZGUW1oTlExVXdSWGhFYWtGTlFtZE9Wa0pCYjFSQ1YwWnVZVmQ0YkUxU1dYZEdRVmxFVmxGUlRFVjNNVzlaV0d4b1NVaHNhRm95YUhSaU0xWjVUVkpKZDBWQldVUldVVkZFUlhkcmVFMXFZM1ZOUXpSM1RHcEZkMVpxUVZGQ1oyTnhhR3RxVDFCUlNVSkNaMVZ5WjFGUlFVTm5Ua05CUVZSVVFVczViSEpVVm10dk9YSnJjVFphV1dOak9VaEVVbHBRTkdJNVV6UjZRVFJMYlRkWldFb3JjMjVVVm1oTWEzcFZNRWh6YlZOWU9WVnVPR3BFYUZKVVQwaEVTMkZtZERoREwzVjFWVms1TXpSMmRVMU9ielJKUTBwNlEwTkJhVTEzWjFsblIwRXhWV1JGVVZOQ1owUkNLM0JJZDNkbGFrVmlUVUpyUjBFeFZVVkNRWGRUVFZNeGIxbFliR2htUkVsMFRXcE5NR1pFVFhSTlZFVjVUVkk0ZDBoUldVdERXa2x0YVZwUWVVeEhVVUpCVVhkUVRYcEJkMDFFWXpGT1ZHYzBUbnBCZDAxRVFYcE5VVEIzUTNkWlJGWlJVVTFFUVZGNFRWUkJkMDFTUlhkRWQxbEVWbEZSWVVSQmFHRlpXRkpxV1ZOQmVFMXFSVmxOUWxsSFFURlZSVVIzZDFCU2JUbDJXa05DUTJSWVRucGhWelZzWXpOTmVrMUNNRWRCTVZWa1JHZFJWMEpDVTJkdFNWZEVObUpRWm1KaVMydHRWSGRQU2xKWWRrbGlTRGxJYWtGbVFtZE9Wa2hUVFVWSFJFRlhaMEpTTWxsSmVqZENjVU56V2pGak1XNWpLMkZ5UzJOeWJWUlhNVXg2UWs5Q1owNVdTRkk0UlZKNlFrWk5SVTluVVdGQkwyaHFNVzlrU0ZKM1QyazRkbVJJVGpCWk0wcHpURzV3YUdSSFRtaE1iV1IyWkdrMWVsbFRPVVJhV0Vvd1VsYzFlV0l5ZUhOTU1WSlVWMnRXU2xSc1dsQlRWVTVHVEZaT01WbHJUa0pNVkVWMVdUTktjMDFKUjNSQ1oyZHlRbWRGUmtKUlkwSkJVVk5DYjBSRFFtNVVRblZDWjJkeVFtZEZSa0pSWTNkQldWcHBZVWhTTUdORWIzWk1NMUo2WkVkT2VXSkROVFpaV0ZKcVdWTTFibUl6V1hWak1rVjJVVEpXZVdSRlZuVmpiVGx6WWtNNVZWVXhjRVpoVnpVeVlqSnNhbHBXVGtSUlZFVjFXbGhvTUZveVJqWmtRelZ1WWpOWmRXSkhPV3BaVjNobVZrWk9ZVkpWYkU5V2F6bEtVVEJWZEZVelZtbFJNRVYwVFZObmVFdFROV3BqYmxGM1MzZFpTVXQzV1VKQ1VWVklUVUZIUjBneWFEQmtTRUUyVEhrNU1HTXpVbXBqYlhkMVpXMUdNRmt5UlhWYU1qa3lURzVPYUV3eU9XcGpNMEYzUkdkWlJGWlNNRkJCVVVndlFrRlJSRUZuWlVGTlFqQkhRVEZWWkVwUlVWZE5RbEZIUTBOelIwRlJWVVpDZDAxRFFtZG5ja0puUlVaQ1VXTkVRWHBCYmtKbmEzSkNaMFZGUVZsSk0wWlJiMFZIYWtGWlRVRnZSME5EYzBkQlVWVkdRbmROUTAxQmIwZERRM05IUVZGVlJrSjNUVVJOUVc5SFEwTnhSMU5OTkRsQ1FVMURRVEJyUVUxRldVTkpVVU5XZDBSTlkzRTJVRThyVFdOdGMwSllWWG92ZGpGSFpHaEhjRGR5Y1ZOaE1rRjRWRXRUZGpnek9FbEJTV2hCVDBKT1JFSjBPU3N6UkZOc2FXcHZWbVo0ZW5Ka1JHZzFNamhYUXpNM2MyMUZaRzlIVjFaeVUzQkhNUT09OlhsajE1THlNQ2dTQzY2T2JuRU8vcVZQZmhTYnMza0RUalduR2hlWWhmU3M9',
                'Content-Type': 'application/json'
            },
            data=payload
        )
        #frappe.msgprint(str(response.text))
        if response.status_code == 200:
            with open(cleared_invoice_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                f.close()
                doc = frappe.get_doc("Sales Invoice",docname)
                doc.cleared=1
                path_components = cleared_invoice_path.split("/private")
                file_path = "/private"+path_components[-1]
                doc.cleared_file = file_path
                doc.save()
                add_attachment(file_path,docname,"cleared_file")
                return True
        return False
@frappe.whitelist()
def generate_qr_invoice(docname):
    zatca_settings = frappe.get_single('ZATCA Settings')
    if not zatca_settings.enable_zatca:
        frappe.msgprint("PLease enable ZATCA settings")
        return False
    sign_invoice_path = zatca_settings.path_for_zatca_files+docname+"_signed.xml"
    invoice_qr_code = zatca_settings.path_for_zatca_files+docname+".png"
   
    try:
        my_env = {**os.environ, 
        'FATOORA_HOME': zatca_settings.zatca_sdk_root_path+'Apps',
        'SDK_CONFIG': zatca_settings.zatca_sdk_root_path+'Configuration/config.json', 
        'PATH': zatca_settings.zatca_sdk_root_path+'Apps/:'+zatca_settings.zatca_sdk_root_path+'Apps/' + os.environ['PATH']}
            
        temp = subprocess.Popen("fatoora -qr -invoice {0} ".format(sign_invoice_path),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,env=my_env
        )
        temp.wait()
        output = str(temp.communicate()[0])

        #frappe.msgprint(str(temp.communicate()))
        base64_str=str(output.split("QR code =")[1])
        img = qrcode.make(base64_str)

        print(type(img))
        print(img.size)
        # <class 'qrcode.image.pil.PilImage'>
        # (290, 290)

        img.save(invoice_qr_code)
        doc = frappe.get_doc("Sales Invoice",docname)
        path_components = invoice_qr_code.split("/private")
        file_path = "/private"+path_components[-1]
        doc.qr_code_file = file_path
        doc.save()
        add_attachment(file_path,docname,"qr_code_file")
        return True
    except subprocess.CalledProcessError as e:
        frappe.msgprint("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return False


def get_invoice_xml_string(docname):
    doc = frappe.get_doc("Sales Invoice",docname)
    invoice_dict = doc.as_dict()
    invoice_xml_string = ""
    invoice_level_discount_string = ""
    items_string = ""

    if invoice_dict.get("discount_amount") > 0:
        invoice_level_discount_string = invoice_level_discount_template.format(
            discount_amount =  invoice_dict.get("discount_amount"),
            tax_percentage = invoice_dict.get("additional_discount_percentage")
        )

    for row in invoice_dict.get("items"):
        item_str = items_template.format(
                idx = row.get("idx"),
                qty = row.get("qty"),
                amount = row.get("amount"),
                rounding_amount = row.get("base_net_amount"),
                item_name = row.get("item_name"),
                rate=row.get("rate"),
                discount_amount = row.get("discount_amount"),
                tax_category ="{tax_category}",
                    tax_amount = "{tax_amount}",
                    tax_percentage = "{tax_percentage}",
            )
        if row.get("item_tax_template"):
            tax_json = json.loads(row.get("item_tax_rate"))
            for k, v in tax_json:
                item_str = item_str.format(
                    tax_category = "S",
                    tax_amount = (tax_json[k]/100)*row.get("base_net_amount"), #to be done
                    tax_percentage = tax_json[k], #to be done
                )
        else:
            item_str = item_str.format( 
                tax_category ="S",
                tax_amount = "0",
                tax_percentage = "0",
            
            )
        items_string+=item_str

    invoice_xml_string = invoice_template.format(
        posting_date = invoice_dict.get("posting_date"),
        delivery_date = invoice_dict.get("posting_date"),
        posting_time = str(invoice_dict.get("posting_time")).split(".")[0],
        customer_tax_id = invoice_dict.get("tax_id") or "12369854769",
        customer_name = invoice_dict.get("customer_name"),
        street = "ST123",
        building = "4562",
        plot = "7862",
        subdivission = "Madina Town",
        city = "Madina",
        postal_code = "12365",
        country = "SA",
        payment_mode_code = "10",
        invoice_level_discount = invoice_level_discount_string,
        total_taxes_and_charges = invoice_dict.get("total_taxes_and_charges"),
        base_net_total_taxes_and_charges = invoice_dict.get("total_taxes_and_charges"),
        sub_total_taxes_and_charges = invoice_dict.get("total_taxes_and_charges"),
        taxable_amount = invoice_dict.get("base_net_total"),
        tax_percentage = (invoice_dict.get("total_taxes_and_charges")/invoice_dict.get("base_net_total"))*100,
        net_total = invoice_dict.get("base_net_total"),
        base_net_total = invoice_dict.get("base_net_total"),
        grand_total = invoice_dict.get("grand_total"),
        total_discount = invoice_dict.get("discount_amount"),
        prepaid_amount = invoice_dict.get("grand_total") - invoice_dict.get("outstanding_amount"),
        outstanding_amount = invoice_dict.get("outstanding_amount"),
        items = items_string
    )
    return invoice_xml_string
        



def add_attachment(file_path,docname,fieldname):
        try:
            
            if frappe.db.exists("File", {
                "file_url": file_path,
                "attached_to_name": docname,
                "attached_to_doctype": "Sales Invoice",
            }):
                
                return

            frappe.get_doc(
                doctype="File",
                file_url=file_path,
                attached_to_name=docname,
                is_private=1,
                attached_to_doctype="Sales Invoice",
                attached_to_field=fieldname,
				folder="Home/Attachments",
            ).insert()
            frappe.msgprint("Done")
        except Exception:
                frappe.log_error(title=_("Error Attaching File"))