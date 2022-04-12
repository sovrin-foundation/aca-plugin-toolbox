"""Connections Tests"""
from acapy_client import Client
from acapy_client.api.connection import (
    get_connections,
    delete_connection,
)
from acapy_client.api.out_of_band import post_out_of_band_create_invitation
from acapy_client.models.invitation_create_request import InvitationCreateRequest
import pytest


@pytest.fixture(autouse=True)
async def clear_connection_state(backchannel: Client, connection_id: str):
    """Clear connections after each test."""
    yield
    connections = await get_connections.asyncio(client=backchannel)
    for connection in connections.results:
        if connection.connection_id != connection_id:
            await delete_connection.asyncio(
                client=backchannel, conn_id=connection.connection_id
            )


@pytest.mark.asyncio
async def test_connection_reuse(
    backchannel: Client,
    endorser_did,
):
    invitation = await post_out_of_band_create_invitation.asyncio(
        client=backchannel,
        json_body=InvitationCreateRequest(
            handshake_protocols=["did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0"],
            use_public_did="true",
        ),
        auto_accept="true",
    )
    {
        "@type": "https://github.com/hyperledger/aries-toolbox/tree/master/docs/admin-connections/0.1/receive-oob-invitation",
        "invitation": invitation.invitation_url,
        "auto_accept": True,
    }
    connections_initial = await get_connections.asyncio(client=backchannel)
    len_conn_initial = len(connections_initial.results)

    # Send another invitation
    invitation = await post_out_of_band_create_invitation.asyncio(
        client=backchannel,
        json_body=InvitationCreateRequest(
            handshake_protocols=["did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/didexchange/1.0"],
            use_public_did="true",
        ),
        auto_accept="true",
    )
    {
        "@type": "https://github.com/hyperledger/aries-toolbox/tree/master/docs/admin-connections/0.1/receive-oob-invitation",
        "invitation": invitation.invitation_url,
        "auto_accept": True,
    }
    connections_final = await get_connections.asyncio(client=backchannel)
    len_conn_final = len(connections_final.results)

    print("Connections initial: ", connections_initial.results)
    print(" ")
    print("Connections final: ", connections_final.results)
    assert len_conn_initial == len_conn_final