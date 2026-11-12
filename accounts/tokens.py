from django.contrib.auth.tokens import PasswordResetTokenGenerator


# Email Verification Token Generator
class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):

        return (
            str(user.pk)
            + str(timestamp)
            + str(user.is_active)
            + str(user.email)
        )


# Create token generator object
email_verification_token = EmailVerificationTokenGenerator()