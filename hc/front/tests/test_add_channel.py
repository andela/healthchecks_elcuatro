from django.test.utils import override_settings

from hc.api.models import Channel, Check
from hc.test import BaseTestCase


@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class AddChannelTestCase(BaseTestCase):

    def test_it_adds_email(self):
        url = "/integrations/add/"
        form = {"kind": "email", "value": "alice@example.org"}

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url, form)

        self.assertRedirects(r, "/integrations/")
        assert Channel.objects.count() == 1

    def test_it_trims_whitespace(self):
        """ Leading and trailing whitespace should get trimmed. """

        url = "/integrations/add/"
        form = {"kind": "email", "value": "   alice@example.org   "}

        self.client.login(username="alice@example.org", password="password")
        self.client.post(url, form)

        q = Channel.objects.filter(value="alice@example.org")
        self.assertEqual(q.count(), 1)

    def test_instructions_work(self):
        self.client.login(username="alice@example.org", password="password")
        kinds = ("email", "webhook", "pd", "pushover", "hipchat", "victorops")
        for frag in kinds:
            url = "/integrations/add_%s/" % frag
            r = self.client.get(url)
            self.assertContains(r, "Integration Settings", status_code=200)

    # Test that the team access works
    def test_team_access_network(self):
        self.team_check = Check(user=self.alice, name="Pair Programming")
        self.team_check.save()
        status = []
        for email in [self.bob.email, "charlie@example.org",
                      "austin.roy@andela.com"]:
            self.client.login(username=email, password="password")
            url = "/checks/{}/log/" .format(self.team_check.code)
            r = self.client.get(url)
            status.append(r.status_code)
        self.assertEqual(status, [200, 403, 403])

    # Test that bad kinds don't work
    def test_bad_kinds_dont_work(self):
        self.client.login(username=self.alice.email, password="password")
        status = []
        for kind in ['email', 'andela', 'pd', 'austin', 'PO']:
            url = '/integrations/add_{}/'.format(kind)
            r = self.client.get(url)
            status.append(r.status_code)
        self.assertEqual(status, [200, 404, 200, 404, 404])
