import openmined_psi



def do_psi(data,enc_data,n):
    server = openmined_psi.server.CreateWithNewKey(reveal_intersection=True)
    setupMsg = server.CreateSetupMessage(fpr=0.1, num_client_inputs=int(n), inputs=data)

    response = server.ProcessRequest(enc_data)

    return setupMsg,response

