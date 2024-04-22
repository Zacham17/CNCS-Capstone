from django.shortcuts import render
from .models import Ticket
from django.http import HttpResponse

# Create your views here.
def index(request):
    tickets = Ticket.objects.order_by('-created_at')[:5]
    
    # Read the contents of the output.txt file
    with open('output.txt', 'r') as file:
        output_content = file.read()
        
    # Format the specific lines
    formatted_output = output_content.replace("Auditbeat Results:", "\n<span class='bold-green'>Auditbeat Results:</span>") \
                                    .replace("Metricbeat Results:", "\n<span class='bold-green'>Metricbeat Results:</span>") \
                                    .replace("Filebeat Results:", "\n<span class='bold-green'>Filebeat Results:</span>") \
                                    .replace("Heartbeat Results:", "\n<span class='bold-green'>Heartbeat Results:</span>")
    
    return render(request, 'index.html', {'tickets': tickets, 'output_content': formatted_output})

def ticket_by_id(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    
    # Read the contents of the output.txt file
    with open('output.txt', 'r') as file:
        output_content = file.read()
        
    # Format the specific lines
    formatted_output = output_content.replace("Auditbeat Results:", "\n<span class='bold-green'>Auditbeat Results:</span>") \
                                    .replace("Metricbeat Results:", "\n<span class='bold-green'>Metricbeat Results:</span>") \
                                    .replace("Filebeat Results:", "\n<span class='bold-green'>Filebeat Results:</span>") \
                                    .replace("Heartbeat Results:", "\n<span class='bold-green'>Heartbeat Results:</span>")
    
    return render(request, 'ticket_by_id.html', {'ticket': ticket, 'output_content': formatted_output})

def refresh_output(request):
    # Read the contents of the output.txt file
    with open('output.txt', 'r') as file:
        output_content = file.read()
        
    # Format the specific lines
    formatted_output = output_content.replace("Auditbeat Results:", "\n<span class='bold-green'>Auditbeat Results:</span>") \
                                    .replace("Metricbeat Results:", "\n<span class='bold-green'>Metricbeat Results:</span>") \
                                    .replace("Filebeat Results:", "\n<span class='bold-green'>Filebeat Results:</span>") \
                                    .replace("Heartbeat Results:", "\n<span class='bold-green'>Heartbeat Results:</span>")
    
    return HttpResponse(formatted_output)
